"""
Chinese Pinyin Conversion Utilities

This module provides utilities for converting Chinese characters to pinyin
(romanized Chinese pronunciation) to enhance search capabilities. Supports both
full pinyin and pinyin initials for flexible search matching.

Usage:
    from shared.pinyin_utils import to_pinyin, to_pinyin_initials, augment_query_with_pinyin

    # Convert Chinese to full pinyin
    pinyin_text = to_pinyin("人工智能")  # "ren gong zhi neng"

    # Get pinyin initials
    initials = to_pinyin_initials("人工智能")  # "rgzn"

    # Augment search query
    variants = augment_query_with_pinyin("ChatGPT 人工智能")
    # Returns: ["ChatGPT 人工智能", "ChatGPT ren gong zhi neng", "ChatGPT rgzn"]
"""

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)

try:
    from pypinyin import pinyin, lazy_pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False
    logger.warning(
        "pypinyin library not available. Pinyin conversion features will be disabled. "
        "Install with: pip install pypinyin>=0.50.0"
    )


def is_chinese_char(char: str) -> bool:
    """
    Check if a character is a Chinese character.

    Args:
        char: Single character to check

    Returns:
        bool: True if character is in CJK Unified Ideographs range
    """
    if not char:
        return False
    code_point = ord(char)
    # CJK Unified Ideographs range (most common Chinese characters)
    return 0x4E00 <= code_point <= 0x9FFF


def contains_chinese(text: str) -> bool:
    """
    Check if text contains any Chinese characters.

    Args:
        text: Text to check

    Returns:
        bool: True if text contains at least one Chinese character
    """
    if not text:
        return False
    return any(is_chinese_char(char) for char in text)


def to_pinyin(
    text: str,
    separator: str = " ",
    tone_marks: bool = False,
    heteronym: bool = False
) -> Optional[str]:
    """
    Convert Chinese text to pinyin with optional tone marks.

    Args:
        text: Chinese text to convert
        separator: Character to use between pinyin syllables (default: space)
        tone_marks: Include tone marks (āáǎà) if True, use tone numbers if False (default: False)
        heteronym: Return multiple pronunciations for characters with multiple readings (default: False)

    Returns:
        str: Pinyin representation of the text, or None if pypinyin unavailable
        Returns original text if no Chinese characters found

    Examples:
        >>> to_pinyin("人工智能")
        "ren gong zhi neng"

        >>> to_pinyin("人工智能", separator="")
        "rengongzhineng"

        >>> to_pinyin("你好世界", tone_marks=True)
        "nǐ hǎo shì jiè"
    """
    if not PYPINYIN_AVAILABLE:
        logger.debug("pypinyin not available, returning original text")
        return text

    if not text or not text.strip():
        return text

    # If no Chinese characters, return original text
    if not contains_chinese(text):
        return text

    try:
        # Choose style based on tone_marks parameter
        style = Style.TONE if tone_marks else Style.NORMAL

        # Convert to pinyin
        result = lazy_pinyin(text, style=style, errors='ignore')

        # Join with separator
        pinyin_text = separator.join(result)

        logger.debug(f"Converted '{text}' to pinyin: '{pinyin_text}'")
        return pinyin_text.lower()

    except Exception as e:
        logger.error(f"Error converting '{text}' to pinyin: {e}")
        return text


def to_pinyin_initials(text: str, separator: str = "") -> Optional[str]:
    """
    Convert Chinese text to pinyin initials (first letter of each syllable).

    This is useful for quick searches where users type only the first letters,
    similar to how "rgzn" could match "人工智能" (ren gong zhi neng).

    Args:
        text: Chinese text to convert
        separator: Character to use between initials (default: no separator)

    Returns:
        str: Pinyin initials, or None if pypinyin unavailable
        Returns original text if no Chinese characters found

    Examples:
        >>> to_pinyin_initials("人工智能")
        "rgzn"

        >>> to_pinyin_initials("机器学习")
        "jqxx"

        >>> to_pinyin_initials("你好", separator="-")
        "n-h"
    """
    if not PYPINYIN_AVAILABLE:
        logger.debug("pypinyin not available, returning original text")
        return text

    if not text or not text.strip():
        return text

    # If no Chinese characters, return original text
    if not contains_chinese(text):
        return text

    try:
        # Get first letter of each pinyin syllable
        result = lazy_pinyin(text, style=Style.FIRST_LETTER, errors='ignore')

        # Join with separator
        initials = separator.join(result)

        logger.debug(f"Converted '{text}' to pinyin initials: '{initials}'")
        return initials.lower()

    except Exception as e:
        logger.error(f"Error converting '{text}' to pinyin initials: {e}")
        return text


def augment_query_with_pinyin(
    query: str,
    include_full_pinyin: bool = True,
    include_initials: bool = True
) -> List[str]:
    """
    Augment a search query with pinyin variations to improve Chinese search.

    This function generates alternative versions of the query with pinyin
    representations of any Chinese text, allowing searches to match both
    Chinese characters and their pinyin equivalents.

    Args:
        query: Original search query (can contain mixed Chinese and English)
        include_full_pinyin: Add full pinyin version (default: True)
        include_initials: Add pinyin initials version (default: True)

    Returns:
        list[str]: List of query variations including original and pinyin versions

    Examples:
        >>> augment_query_with_pinyin("ChatGPT 人工智能")
        ["ChatGPT 人工智能", "ChatGPT ren gong zhi neng", "ChatGPT rgzn"]

        >>> augment_query_with_pinyin("对话AI")
        ["对话AI", "dui hua AI", "dhAI"]

        >>> augment_query_with_pinyin("Hello World")  # No Chinese
        ["Hello World"]
    """
    if not query or not query.strip():
        return [query]

    query = query.strip()
    variations = [query]  # Always include original query

    # If no Chinese characters, no need to augment
    if not contains_chinese(query):
        return variations

    if not PYPINYIN_AVAILABLE:
        logger.debug("pypinyin not available, returning original query only")
        return variations

    try:
        # Add full pinyin version
        if include_full_pinyin:
            full_pinyin = to_pinyin(query, separator=" ")
            if full_pinyin and full_pinyin != query:
                variations.append(full_pinyin)

        # Add pinyin initials version
        if include_initials:
            initials = to_pinyin_initials(query, separator="")
            if initials and initials != query:
                variations.append(initials)

        logger.debug(f"Augmented query '{query}' with {len(variations)} variations")
        return variations

    except Exception as e:
        logger.error(f"Error augmenting query '{query}' with pinyin: {e}")
        return variations


def extract_chinese_segments(text: str) -> List[tuple[str, bool]]:
    """
    Split text into segments of Chinese and non-Chinese characters.

    Args:
        text: Text to segment

    Returns:
        list[tuple[str, bool]]: List of (segment, is_chinese) tuples

    Examples:
        >>> extract_chinese_segments("ChatGPT人工智能API")
        [("ChatGPT", False), ("人工智能", True), ("API", False)]

        >>> extract_chinese_segments("100%中文")
        [("100%", False), ("中文", True)]
    """
    if not text:
        return []

    segments = []
    current_segment = []
    current_is_chinese = None

    for char in text:
        char_is_chinese = is_chinese_char(char)

        if current_is_chinese is None:
            # First character
            current_is_chinese = char_is_chinese
            current_segment.append(char)
        elif char_is_chinese == current_is_chinese:
            # Same type, continue current segment
            current_segment.append(char)
        else:
            # Type changed, save current segment and start new one
            if current_segment:
                segments.append(("".join(current_segment), current_is_chinese))
            current_segment = [char]
            current_is_chinese = char_is_chinese

    # Add final segment
    if current_segment:
        segments.append(("".join(current_segment), current_is_chinese))

    return segments


def mixed_text_to_pinyin(text: str, separator: str = " ") -> str:
    """
    Convert only the Chinese portions of mixed Chinese-English text to pinyin,
    preserving non-Chinese text as-is.

    Args:
        text: Mixed Chinese and non-Chinese text
        separator: Separator between pinyin syllables (default: space)

    Returns:
        str: Text with Chinese converted to pinyin, non-Chinese preserved

    Examples:
        >>> mixed_text_to_pinyin("ChatGPT人工智能API")
        "ChatGPT ren gong zhi neng API"

        >>> mixed_text_to_pinyin("使用AI技术")
        "shi yong AI ji shu"
    """
    if not text or not PYPINYIN_AVAILABLE:
        return text

    segments = extract_chinese_segments(text)
    result_parts = []

    for segment, is_chinese in segments:
        if is_chinese:
            # Convert Chinese segment to pinyin
            pinyin_segment = to_pinyin(segment, separator=separator)
            result_parts.append(pinyin_segment if pinyin_segment else segment)
        else:
            # Keep non-Chinese as-is
            result_parts.append(segment)

    # Join with space, but clean up multiple spaces
    result = " ".join(result_parts)
    result = re.sub(r'\s+', ' ', result).strip()

    return result


def get_library_info() -> dict:
    """
    Get information about the pypinyin library availability and version.

    Returns:
        dict: Library availability and version information
    """
    info = {
        "available": PYPINYIN_AVAILABLE,
        "version": None,
        "supported_features": []
    }

    if PYPINYIN_AVAILABLE:
        try:
            import pypinyin
            info["version"] = getattr(pypinyin, '__version__', 'unknown')
            info["supported_features"] = [
                "full_pinyin",
                "pinyin_initials",
                "tone_marks",
                "mixed_text_conversion"
            ]
        except Exception as e:
            logger.warning(f"Error getting pypinyin info: {e}")

    return info


# Example usage and validation
if __name__ == "__main__":
    print("=== Chinese Pinyin Conversion Utilities ===\n")

    # Library info
    info = get_library_info()
    print(f"pypinyin available: {info['available']}")
    if info['version']:
        print(f"pypinyin version: {info['version']}")
    print()

    if not PYPINYIN_AVAILABLE:
        print("⚠️  pypinyin not installed. Install with: pip install pypinyin>=0.50.0")
        exit(1)

    # Test basic conversion
    print("=== Basic Pinyin Conversion ===")
    test_words = ["人工智能", "机器学习", "深度学习", "自然语言处理", "ChatGPT"]
    for word in test_words:
        full = to_pinyin(word)
        initials = to_pinyin_initials(word)
        print(f"{word:12} -> full: {full:30} initials: {initials}")
    print()

    # Test mixed text
    print("=== Mixed Text Conversion ===")
    mixed_texts = [
        "ChatGPT是一个人工智能工具",
        "使用AI进行图像生成",
        "100%中文支持",
        "Hello世界"
    ]
    for text in mixed_texts:
        converted = mixed_text_to_pinyin(text)
        print(f"{text:35} -> {converted}")
    print()

    # Test query augmentation
    print("=== Query Augmentation ===")
    test_queries = [
        "对话AI",
        "人工智能助手",
        "ChatGPT 中文",
        "图像生成工具"
    ]
    for query in test_queries:
        variants = augment_query_with_pinyin(query)
        print(f"\nOriginal: {query}")
        for i, variant in enumerate(variants, 1):
            print(f"  {i}. {variant}")
    print()

    # Test segmentation
    print("=== Text Segmentation ===")
    test_texts = [
        "ChatGPT人工智能API",
        "使用AI技术开发",
        "100%支持中文"
    ]
    for text in test_texts:
        segments = extract_chinese_segments(text)
        print(f"\n{text}")
        for segment, is_chinese in segments:
            segment_type = "Chinese" if is_chinese else "Non-Chinese"
            print(f"  '{segment}' ({segment_type})")
    print()

    # Test tone marks
    print("=== Tone Marks ===")
    test_tones = ["你好", "世界", "谢谢", "再见"]
    for word in test_tones:
        with_tones = to_pinyin(word, tone_marks=True)
        without_tones = to_pinyin(word, tone_marks=False)
        print(f"{word:8} -> with tones: {with_tones:20} without: {without_tones}")
