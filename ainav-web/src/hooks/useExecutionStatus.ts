/**
 * React hook for managing execution step state
 *
 * Provides state management for tracking node execution status in real-time,
 * handling WebSocket updates, and managing step-by-step execution data.
 */

import { useState, useCallback, useMemo } from "react";
import type {
  ExecutionStep,
  ExecutionStepUpdate,
  NodeExecutionStatus,
} from "@/lib/types";

/**
 * Map of node IDs to their execution step data
 */
export type ExecutionStepsMap = Map<string, ExecutionStep>;

/**
 * State management for execution tracking
 */
export interface ExecutionStatusState {
  /** Map of node_id to execution step data */
  steps: ExecutionStepsMap;
  /** Current execution status */
  executionStatus: "idle" | "pending" | "running" | "completed" | "failed" | "cancelled";
  /** Active/currently running node ID */
  activeNodeId: string | null;
  /** Total token usage across all steps */
  totalTokens: number;
  /** Execution start time */
  startedAt: string | null;
  /** Execution completion time */
  completedAt: string | null;
}

/**
 * Actions for updating execution state
 */
export interface ExecutionStatusActions {
  /** Initialize steps from execution details */
  initializeSteps: (steps: ExecutionStep[]) => void;
  /** Update a single step from WebSocket message */
  updateStep: (update: ExecutionStepUpdate) => void;
  /** Get step data for a specific node */
  getStep: (nodeId: string) => ExecutionStep | undefined;
  /** Get status for a specific node */
  getNodeStatus: (nodeId: string) => NodeExecutionStatus;
  /** Reset all execution state */
  reset: () => void;
  /** Mark execution as started */
  start: () => void;
  /** Mark execution as completed */
  complete: () => void;
  /** Mark execution as failed */
  fail: (errorMessage?: string) => void;
}

/**
 * Return type combining state and actions
 */
export interface UseExecutionStatusReturn extends ExecutionStatusState, ExecutionStatusActions {}

/**
 * Initial state
 */
const initialState: ExecutionStatusState = {
  steps: new Map(),
  executionStatus: "idle",
  activeNodeId: null,
  totalTokens: 0,
  startedAt: null,
  completedAt: null,
};

/**
 * Hook for managing execution status and step tracking
 *
 * @example
 * ```tsx
 * const execution = useExecutionStatus();
 *
 * // Initialize from API response
 * useEffect(() => {
 *   if (executionDetails?.execution_steps) {
 *     execution.initializeSteps(executionDetails.execution_steps);
 *   }
 * }, [executionDetails]);
 *
 * // Handle WebSocket updates
 * useEffect(() => {
 *   ws.onmessage = (event) => {
 *     const update = JSON.parse(event.data);
 *     execution.updateStep(update);
 *   };
 * }, [ws]);
 *
 * // Get status for a node
 * const nodeStatus = execution.getNodeStatus('node-1');
 * ```
 */
export function useExecutionStatus(): UseExecutionStatusReturn {
  const [state, setState] = useState<ExecutionStatusState>(initialState);

  /**
   * Initialize steps from execution details (e.g., when loading existing execution)
   */
  const initializeSteps = useCallback((steps: ExecutionStep[]) => {
    const stepsMap = new Map<string, ExecutionStep>();
    let totalTokens = 0;

    steps.forEach((step) => {
      stepsMap.set(step.node_id, step);
      if (step.token_usage?.total) {
        totalTokens += step.token_usage.total;
      }
    });

    setState((prev) => ({
      ...prev,
      steps: stepsMap,
      totalTokens,
    }));
  }, []);

  /**
   * Update a single step from WebSocket message
   */
  const updateStep = useCallback((update: ExecutionStepUpdate) => {
    setState((prev) => {
      const newSteps = new Map(prev.steps);
      const existingStep = newSteps.get(update.node_id);

      // Merge update with existing step data
      const updatedStep: ExecutionStep = {
        node_id: update.node_id,
        status: update.status,
        input_data: update.input_data ?? existingStep?.input_data,
        output_data: update.output_data ?? existingStep?.output_data,
        error_message: update.error_message ?? existingStep?.error_message,
        token_usage: update.token_usage ?? existingStep?.token_usage,
        started_at: existingStep?.started_at ?? (
          update.status === NodeExecutionStatus.RUNNING ? update.timestamp : undefined
        ),
        completed_at: (
          update.status === NodeExecutionStatus.SUCCESS ||
          update.status === NodeExecutionStatus.ERROR ||
          update.status === NodeExecutionStatus.FAILED ||
          update.status === NodeExecutionStatus.COMPLETED
        ) ? update.timestamp : existingStep?.completed_at,
      };

      newSteps.set(update.node_id, updatedStep);

      // Calculate new total tokens
      let totalTokens = 0;
      newSteps.forEach((step) => {
        if (step.token_usage?.total) {
          totalTokens += step.token_usage.total;
        }
      });

      // Determine active node (currently running)
      let activeNodeId: string | null = null;
      newSteps.forEach((step) => {
        if (step.status === NodeExecutionStatus.RUNNING) {
          activeNodeId = step.node_id;
        }
      });

      return {
        ...prev,
        steps: newSteps,
        totalTokens,
        activeNodeId,
      };
    });
  }, []);

  /**
   * Get step data for a specific node
   */
  const getStep = useCallback((nodeId: string): ExecutionStep | undefined => {
    return state.steps.get(nodeId);
  }, [state.steps]);

  /**
   * Get status for a specific node (returns PENDING if not found)
   */
  const getNodeStatus = useCallback((nodeId: string): NodeExecutionStatus => {
    const step = state.steps.get(nodeId);
    return step?.status ?? NodeExecutionStatus.PENDING;
  }, [state.steps]);

  /**
   * Reset all execution state
   */
  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  /**
   * Mark execution as started
   */
  const start = useCallback(() => {
    setState((prev) => ({
      ...prev,
      executionStatus: "running",
      startedAt: new Date().toISOString(),
      completedAt: null,
    }));
  }, []);

  /**
   * Mark execution as completed
   */
  const complete = useCallback(() => {
    setState((prev) => ({
      ...prev,
      executionStatus: "completed",
      completedAt: new Date().toISOString(),
      activeNodeId: null,
    }));
  }, []);

  /**
   * Mark execution as failed
   */
  const fail = useCallback((errorMessage?: string) => {
    setState((prev) => ({
      ...prev,
      executionStatus: "failed",
      completedAt: new Date().toISOString(),
      activeNodeId: null,
    }));
  }, []);

  // Return combined state and actions
  return useMemo(() => ({
    ...state,
    initializeSteps,
    updateStep,
    getStep,
    getNodeStatus,
    reset,
    start,
    complete,
    fail,
  }), [
    state,
    initializeSteps,
    updateStep,
    getStep,
    getNodeStatus,
    reset,
    start,
    complete,
    fail,
  ]);
}
