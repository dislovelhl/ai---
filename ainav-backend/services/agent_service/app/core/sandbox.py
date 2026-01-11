"""
Code Execution Sandbox

Provides a secure environment for executing user-provided Python code
using RestrictedPython. Prevents access to dangerous operations like
file I/O, network access, and system calls.
"""
import logging
import signal
import sys
from typing import Any, Dict, Optional
from contextlib import contextmanager

from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence
from RestrictedPython.Eval import default_guarded_getattr, default_guarded_getitem
from RestrictedPython.PrintCollector import PrintCollector

logger = logging.getLogger(__name__)

# Maximum execution time in seconds
MAX_EXECUTION_TIME = 5

# Safe builtins - only allow non-dangerous functions
SAFE_BUILTINS = {
    **safe_builtins,
    # Math operations
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
    'sum': sum,
    'pow': pow,
    'divmod': divmod,
    # Type conversions
    'int': int,
    'float': float,
    'str': str,
    'bool': bool,
    'list': list,
    'dict': dict,
    'tuple': tuple,
    'set': set,
    # String operations
    'len': len,
    'sorted': sorted,
    'reversed': reversed,
    'enumerate': enumerate,
    'zip': zip,
    'range': range,
    'map': map,
    'filter': filter,
    # Type checking
    'isinstance': isinstance,
    'type': type,
    # None and booleans
    'None': None,
    'True': True,
    'False': False,
}

# Explicitly blocked operations
BLOCKED_NAMES = {
    'open', 'file', 'exec', 'eval', 'compile', 'execfile',
    '__import__', 'import', 'input', 'raw_input',
    'os', 'sys', 'subprocess', 'socket', 'requests', 'urllib',
    'exit', 'quit', 'globals', 'locals', 'vars', 'dir',
    'getattr', 'setattr', 'delattr', 'hasattr',
}


class TimeoutError(Exception):
    """Raised when code execution exceeds time limit."""
    pass


class SandboxError(Exception):
    """Raised when sandbox detects unsafe operations."""
    pass


@contextmanager
def timeout(seconds: int):
    """Context manager for execution timeout."""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Execution exceeded {seconds} second limit")
    
    # Only works on Unix-like systems
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows fallback - no timeout enforcement
        yield


class CodeSandbox:
    """
    Secure Python code execution sandbox.
    
    Uses RestrictedPython to compile code with safety restrictions,
    limiting access to dangerous operations.
    """
    
    def __init__(self, max_execution_time: int = MAX_EXECUTION_TIME):
        self.max_execution_time = max_execution_time
    
    def _validate_code(self, code: str) -> None:
        """Pre-validate code for obviously dangerous patterns."""
        import re
        
        for blocked in BLOCKED_NAMES:
            # Use word boundaries to avoid false positives (e.g., "input_data" containing "input")
            if re.search(rf'\b{blocked}\b', code, re.IGNORECASE):
                raise SandboxError(f"Blocked operation detected: {blocked}")
        
        # Check for attribute access patterns that could bypass restrictions
        dangerous_patterns = [
            '__class__', '__base__', '__subclasses__', '__mro__',
            '__globals__', '__code__', '__builtins__',
        ]
        for pattern in dangerous_patterns:
            if pattern in code:
                raise SandboxError(f"Dangerous pattern detected: {pattern}")
    
    def execute(
        self, 
        code: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            context: Variables to make available to the code
            
        Returns:
            Dict containing 'result' (last expression) and 'output' (print statements)
        """
        # Pre-validation
        self._validate_code(code)
        
        # Compile with restrictions
        try:
            byte_code = compile_restricted(
                code,
                filename='<sandbox>',
                mode='exec'
            )
        except SyntaxError as e:
            raise SandboxError(f"Syntax error in code: {e}")
        
        # Check for compilation errors (RestrictedPython may return None on error)
        if byte_code is None:
            raise SandboxError("Compilation failed - code contains restricted operations")
        
        # Prepare execution environment with PrintCollector
        exec_globals = {
            '__builtins__': SAFE_BUILTINS,
            '_getattr_': default_guarded_getattr,
            '_getitem_': default_guarded_getitem,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '_unpack_sequence_': guarded_unpack_sequence,
            '_getiter_': iter,
            '_write_': lambda x: x,  # Allow writes to local scope
            '_print_': PrintCollector,  # Use PrintCollector class
            '_getiter_': iter,
            'result': None,  # Placeholder for result
        }
        
        # Add user-provided context
        if context:
            for key, value in context.items():
                if key not in BLOCKED_NAMES and not key.startswith('_'):
                    exec_globals[key] = value
        
        # Execute with timeout
        try:
            with timeout(self.max_execution_time):
                exec(byte_code, exec_globals)
        except TimeoutError:
            raise SandboxError(f"Execution timeout after {self.max_execution_time} seconds")
        except Exception as e:
            raise SandboxError(f"Execution error: {type(e).__name__}: {e}")
        
        # Collect printed output from PrintCollector
        printed_output = ""
        if '_print' in exec_globals and hasattr(exec_globals['_print'], 'printed'):
            printed_output = '\n'.join(exec_globals['_print'].printed)
        
        return {
            'result': exec_globals.get('result'),
            'output': printed_output,
            'variables': {
                k: v for k, v in exec_globals.items()
                if not k.startswith('_') and k not in SAFE_BUILTINS
            }
        }


# Singleton instance
sandbox = CodeSandbox()
