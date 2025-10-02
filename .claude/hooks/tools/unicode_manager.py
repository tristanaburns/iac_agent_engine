#!/usr/bin/env python3
"""
Unicode Manager Module.

Provides safe Unicode and emoji cleanup functionality for Python codebases.
This module handles Unicode character detection, replacement, and cleanup
while preserving code formatting and functionality.

Author: System
Version: 1.0.0
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class UnicodeManager:
    """
    Manages Unicode character cleanup and replacement in source files.

    Provides safe, configurable Unicode character handling with backup
    capabilities and format preservation.
    """

    def __init__(self, config_path: Optional[str] = None, mode: str = "delete") -> None:
        """
        Initialize Unicode Manager.

        Args:
            config_path: Optional path to configuration file
            mode: Operation mode - "delete" (default) or "replace"
        """
        self.config_path = config_path
        self.mode = mode  # "delete" or "replace"
        self.config: Dict[str, Any] = self._load_default_config()
        self.stats: Dict[str, int] = {
            "files_processed": 0,
            "files_modified": 0,
            "unicode_characters_replaced": 0,
            "unicode_characters_deleted": 0,
            "backups_created": 0,
        }
        # Create backup directory relative to .claude directory
        self.backup_dir = (
            Path(__file__).parent.parent.parent / "backups" / "unicode_cleanup"
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        if config_path and Path(config_path).exists():
            self._load_config(config_path)

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            "file_extensions": [".py", ".md", ".txt", ".yml", ".yaml", ".json"],
            "excluded_dirs": [
                "__pycache__",
                ".git",
                ".pytest_cache",
                "node_modules",
                ".venv",
                "venv",
                ".env",
                "dist",
                "build",
                ".mypy_cache",
                "backups",
                ".tox",
                "site-packages",
            ],
            "unicode_replacements": {
                "->": "->",
                "[OK]": "[OK]",
                "[ERROR]": "[ERROR]",
                "[WARNING]": "[WARNING]",
                "[NOTE]": "[NOTE]",
                "[CONFIG]": "[CONFIG]",
                "[TARGET]": "[TARGET]",
                "[TIP]": "[TIP]",
                "[SEARCH]": "[SEARCH]",
                "[DATA]": "[DATA]",
                "[SECURE]": "[SECURE]",
                "*": "*",
                "[SUCCESS]": "[SUCCESS]",
                "[ALERT]": "[ALERT]",
                "[REFRESH]": "[REFRESH]",
            },
            "preserve_formatting": True,
            "create_backups": True,
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "mode": "delete",  # Default mode: "delete" or "replace"
        }

    def _load_config(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Merge with defaults
            self.config.update(user_config)
            logger.info(f"Loaded configuration from: {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            logger.info("Using default configuration")

    def _should_process_file(self, file_path: Path) -> bool:
        """
        Determine if file should be processed.

        Args:
            file_path: Path to check

        Returns:
            True if file should be processed
        """
        # Ensure file_path is a Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        # Skip backup files (inert files ending with .backup)
        if file_path.name.endswith(".backup"):
            return False

        # Check file extension
        if file_path.suffix not in self.config["file_extensions"]:
            return False

        # Check if in excluded directory
        for part in file_path.parts:
            if part in self.config["excluded_dirs"]:
                return False

        # Check file size
        try:
            if file_path.stat().st_size > self.config["max_file_size"]:
                return False
        except OSError:
            return False

        return True

    def _detect_unicode_chars(self, content: str) -> List[Tuple[str, int]]:
        """
        Detect Unicode characters in content.

        Args:
            content: Text content to analyze

        Returns:
            List of (character, count) tuples
        """
        unicode_chars: Dict[str, int] = {}

        for char in content:
            if ord(char) > 127:  # Non-ASCII character
                unicode_chars[char] = unicode_chars.get(char, 0) + 1

        return list(unicode_chars.items())

    def _delete_unicode_chars(self, content: str) -> Tuple[str, int]:
        """
        Delete Unicode characters while preserving formatting.

        Args:
            content: Original content

        Returns:
            Tuple of (modified_content, deletion_count)
        """
        new_content = []
        deletion_count = 0

        for char in content:
            if ord(char) > 127:
                # Skip unicode character (delete it)
                deletion_count += 1
                # Don't append anything - effectively deleting the character
            else:
                new_content.append(char)

        if deletion_count > 0:
            return "".join(new_content), deletion_count
        else:
            return content, 0

    def _get_emoji_replacements(self) -> Dict[str, str]:
        """
        Get comprehensive emoji to ASCII replacements mapping.

        Returns:
            Dictionary mapping emoji Unicode strings to ASCII replacements
        """
        # Common LLM emoji replacements mapping using unicode escape sequences
        return {
            "\U00002705": "[OK]",  # [OK] Check mark
            "\U0000274c": "[X]",  # [X] Cross mark
            "\U00002757": "[WARNING]",  # [WARNING] Exclamation mark
            "\U0001f680": "[LAUNCH]",  # [LAUNCH] Rocket
            "\U0001f4a1": "[IDEA]",  # [IDEA] Light bulb
            "\U0001f527": "[TOOL]",  # [TOOL] Wrench
            "\U0001f4dd": "[NOTE]",  # [NOTE] Memo
            "\U0001f4da": "[DOCS]",  # [DOCS] Books
            "\U0001f3af": "[TARGET]",  # [TARGET] Direct hit
            "\U0001f50d": "[SEARCH]",  # [ZOOM] Magnifying glass
            "\U0001f4bb": "[CODE]",  # [CODE] Laptop
            "\U0001f41b": "[BUG]",  # [BUG] Bug
            "\U0001f195": "[NEW]",  # [NEW] New button
            "\U0001f525": "[FIRE]",  # [FIRE] Fire
            "\U00002b50": "[STAR]",  # [STAR] Star
            "\U0001f4e6": "[PACKAGE]",  # [ENCRYPTED] Package
            "\U0001f6a8": "[ALERT]",  # [ALERT] Police car light
            "\U00002714": "[SUCCESS]",  # [SUCCESS]? Check mark
            "\U0001f44d": "[GOOD]",  # [GOOD] Thumbs up
            "\U0001f44e": "[BAD]",  # [BAD] Thumbs down
            "\U000026a1": "[LIGHTNING]",  # [LIGHTNING] Lightning bolt
            "\U0001f512": "[SECURE]",  # [SECURE] Lock
            "\U0001f513": "[UNSECURE]",  # [UNSECURE] Unlock
            "\U0001f511": "[KEY]",  # [KEY] Key
            "\U0001f4ca": "[DATA]",  # [DATA] Bar chart
            "\U00002b06": "[UP]",  # [UP]? Up arrow
            "\U00002b07": "[DOWN]",  # [DOWN]? Down arrow
            "\U0001f6e0": "[BUILD]",  # [BUILD]? Hammer and wrench
            "\U0001f528": "[FIX]",  # [FIX] Hammer
            "\U0001f514": "[NOTIFICATION]",  # [NOTIFICATION] Bell
            "\U0001f310": "[WEB]",  # [WEB] Globe with meridians
            "\U0001f4be": "[SAVE]",  # [SAVE] Floppy disk
            "\U0001f4c1": "[FOLDER]",  # [FOLDER] File folder
            "\U0001f4c4": "[FILE]",  # [FILE] Page facing up
            "\U0001f517": "[LINK]",  # [LINK] Link
            "\U00002702": "[CUT]",  # [CUT]? Scissors
            "\U0001f4cb": "[CLIPBOARD]",  # [CLIPBOARD] Clipboard
            "\U0001f504": "[REFRESH]",  # [REFRESH] Counterclockwise arrows
            "\U000023f0": "[WAIT]",  # [WAIT] Alarm clock
            "\U0001f552": "[TIME]",  # [TIME] Clock
            "\U00002709": "[EMAIL]",  # [EMAIL]? Envelope
            "\U0001f4ac": "[CHAT]",  # [CHAT] Speech balloon
            "\U0001f4ad": "[COMMENT]",  # [COMMENT] Thought balloon
            "\U0001f914": "[THOUGHT]",  # [THINK] Thinking face
            "\U00002753": "[QUESTION]",  # [QUESTION] Question mark
            "\U00002755": "[IMPORTANT]",  # [IMPORTANT] Exclamation mark
            "\U0001f4aa": "[STRONG]",  # [STRONG] Flexed biceps
            "\U0001f3a8": "[DESIGN]",  # [DESIGN] Artist palette
            "\U0001f3c6": "[AWARD]",  # [AWARD] Trophy
            "\U0001f947": "[FIRST]",  # [FIRST] 1st place medal
            "\U0001f948": "[SECOND]",  # [SECOND] 2nd place medal
            "\U0001f949": "[THIRD]",  # [THIRD] 3rd place medal
            "\U0001f4f1": "[MOBILE]",  # [MOBILE] Mobile phone
            "\U0001f5a5": "[DESKTOP]",  # [DESKTOP]? Desktop computer
            "\U00002699": "[CONFIG]",  # [CONFIG]? Gear
            "\U0001f4cf": "[MEASURE]",  # [MEASURE] Ruler
            "\U0001f9ea": "[TEST]",  # [TEST] Test tube
            "\U0001f9e9": "[COMPLEX]",  # [COMPLEX] Puzzle piece
            "\U0001f50e": "[ANALYZE]",  # [ANALYZE] Magnifying glass right
            "\U0001f31f": "[PREMIUM]",  # [PREMIUM] Glowing star
            "\U0001f4c8": "[STATUS]",  # [STATUS] Chart increasing
            "\U0001f3ae": "[GAME]",  # [GAME] Video game
            "\U0001f3ac": "[ACTION]",  # [ACTION] Clapper board
            "\U0001f4f7": "[PHOTO]",  # [PHOTO] Camera
            "\U0001f3b5": "[MUSIC]",  # [MUSIC] Musical note
            "\U0001f3a4": "[MIC]",  # [MIC] Microphone
            "\U0001f50a": "[SOUND]",  # [SOUND] Speaker high volume
            "\U0001f507": "[MUTE]",  # [MUTE] Muted speaker
            "\U0001f4e2": "[ANNOUNCE]",  # [ANNOUNCE] Loudspeaker
            "\U0001f4e1": "[BROADCAST]",  # [BROADCAST] Satellite antenna
            "\U0001f5c4": "[ARCHIVE]",  # [ARCHIVE]? File cabinet
            "\U0001f5c3": "[STORAGE]",  # [STORAGE]? Card file box
            "\U0001f5d1": "[DELETE]",  # [DELETE]? Wastebasket
            "\U0001f4cc": "[PIN]",  # [PIN] Pushpin
            "\U0001f4cd": "[LOCATION]",  # [LOCATION] Round pushpin
            "\U0001f30d": "[GLOBAL]",  # [GLOBAL] Earth globe Europe-Africa
            "\U0001f30e": "[AMERICAS]",  # [AMERICAS] Earth globe Americas
            "\U0001f30f": "[ASIA]",  # [ASIA] Earth globe Asia-Australia
            "\U0001f6aa": "[DOOR]",  # [DOOR] Door
            "\U0001f510": "[LOCKED]",  # [LOCKED] Closed lock with key
            "\U0001f4b0": "[MONEY]",  # [MONEY] Money bag
            "\U0001f4b3": "[PAYMENT]",  # [PAYMENT] Credit card
            "\U0001f4f6": "[SIGNAL]",  # [SIGNAL] Antenna bars
            "\U0001f6f0": "[SATELLITE]",  # [SATELLITE]? Satellite
            "\U0001f681": "[HELICOPTER]",  # [HELICOPTER] Helicopter
            "\U00002708": "[PLANE]",  # [PLANE]? Airplane
            "\U0001f686": "[TRAIN]",  # [TRAIN] Train
            "\U0001f697": "[CAR]",  # [CAR] Automobile
            "\U0001f3c3": "[RUN]",  # [RUN] Person running
            "\U000025b6": "[PLAY]",  # >? Play button
            "\U000023f8": "[PAUSE]",  # [PAUSE]? Pause button
            "\U000023f9": "[STOP]",  # [STOP]? Stop button
            "\U000023fa": "[RECORD]",  # [RECORD]? Record button
            "\U0001f534": "[RED]",  # [RED] Red circle
            "\U0001f7e2": "[GREEN]",  # [GREEN] Green circle
            "\U0001f7e1": "[YELLOW]",  # [YELLOW] Yellow circle
            "\U0001f535": "[BLUE]",  # [BLUE] Blue circle
            "\U0001f7e0": "[ORANGE]",  # [ORANGE] Orange circle
            "\U0001f7e3": "[PURPLE]",  # [PURPLE] Purple circle
            "\U000026ab": "[BLACK]",  # [BLACK] Black circle
            "\U000026aa": "[WHITE]",  # [WHITE] White circle
            "\U0001f48e": "[DIAMOND]",  # [DIAMOND] Gem stone
            "\U00002192": "->",  # -> Right arrow
            "\U00002190": "<-",  # <- Left arrow
            "\U00002191": "^",  # ^ Up arrow
            "\U00002193": "v",  # v Down arrow
            "\U000021a9": "[RETURN]",  # [RETURN]? Return arrow
            "\U000027a1": "[FORWARD]",  # [FORWARD]? Forward arrow
            "\U0001f500": "[SHUFFLE]",  # [SHUFFLE] Shuffle arrows
            "\U0001f501": "[REPEAT]",  # [REPEAT] Repeat arrows
            "\U0001f502": "[REPEAT1]",  # [REPEAT1] Repeat one arrow
            "\U000025c0": "<",  # < Reverse
            "\U000023ea": "<<",  # << Fast reverse
            "\U000023e9": ">>",  # >> Fast forward
        }

    def _get_emoticon_replacements(self) -> Dict[str, str]:
        """
        Get emoticon and face emoji replacements.

        Returns:
            Dictionary mapping face emoji Unicode strings to ASCII emoticons
        """
        return {
            "\U0001f603": ":)",  # :) Smiley
            "\U0001f61e": ":(",  # :( Disappointed face
            "\U0001f620": ">:(",  # >:( Angry face
            "\U0001f60e": "B)",  # B) Sunglasses face
            "\U0001f440": "[LOOK]",  # [LOOK] Eyes
            "\U0001f44b": "[WAVE]",  # [WAVE] Waving hand
            "\U0001f91d": "[HANDSHAKE]",  # [HANDSHAKE] Handshake
            "\U0001f44f": "[CLAP]",  # [CLAP] Clapping hands
            "\U0001f64f": "[PRAY]",  # [PRAY] Praying hands
            "\U0001f9e0": "[BRAIN]",  # [BRAIN] Brain
            "\U00002764": "[HEART]",  # [HEART]? Red heart
            "\U0001f494": "[BROKEN]",  # [BROKEN] Broken heart
            "\U0001f308": "[RAINBOW]",  # [RAINBOW] Rainbow
            "\U00002600": "[SUN]",  # [SUN]? Sun
            "\U0001f319": "[MOON]",  # [MOON] Crescent moon
            "\U0001f4a7": "[DROP]",  # [DROP] Droplet
            "\U0001f30a": "[WATER_WAVE]",  # [WATER_WAVE] Water wave
            "\U0001f343": "[LEAF]",  # [LEAF] Leaf fluttering
            "\U0001f338": "[FLOWER]",  # [FLOWER] Cherry blossom
            "\U0001f600": ":)",  # :) Grinning face
            "\U0001f60a": ":)",  # :) Smiling face
            "\U0001f642": ":)",  # :) Slightly smiling
            "\U0001f609": ";)",  # ;) Winking face
            "\U0001f61c": ";P",  # ;P Face with tongue
            "\U0001f923": "XD",  # XD Rolling on floor laughing
            "\U0001f602": ":D",  # :D Face with tears of joy
            "\U0001f604": ":D",  # :D Grinning face with smiling eyes
            "\U0001f605": "XD",  # XD Grinning face with sweat
            "\U0001f606": "XD",  # XD Grinning squinting face
            "\U0001f60d": "<3",  # <3 Heart eyes
            "\U0001f618": ":-*",  # :-* Face blowing kiss
            "\U0001f61a": ":-*",  # :-* Kissing face with closed eyes
            "\U0001f617": ":-*",  # :-* Kissing face
            "\U0001f619": ":-*",  # :-* Kissing face with smiling eyes
            "\U0001f61b": ":P",  # :P Face with tongue
            "\U0001f61d": "XP",  # XP Squinting face with tongue
            "\U0001f610": ":|",  # :| Neutral face
            "\U0001f611": ":|",  # :| Expressionless face
            "\U0001f636": ":|",  # :| Face without mouth
            "\U0001f60f": ":]",  # :] Smirking face
            "\U0001f612": ":/",  # :/ Unamused face
            "\U0001f644": ":/",  # :/ Face with rolling eyes
            "\U0001f62c": ":S",  # :S Grimacing face
            "\U0001f925": "0.0",  # 0.0 Lying face
            "\U0001f60c": "z_z",  # z_z Relieved face
            "\U0001f614": ":(",  # :( Pensive face
            "\U0001f62a": "-.-",  # -.- Sleepy face
            "\U0001f924": "Achoo!",  # Achoo! Drooling face
            "\U0001f634": "Zzz",  # Zzz Sleeping face
            "\U0001f637": ":X",  # :X Face with medical mask
            "\U0001f912": ":###",  # :### Face with thermometer
            "\U0001f915": ":###",  # :### Face with head bandage
            "\U0001f922": "X(",  # X( Nauseated face
            "\U0001f92e": "X|",  # X| Face vomiting
            "\U0001f927": "Achoo!",  # Achoo! Sneezing face
            "\U0001f975": "@_@",  # @_@ Hot face
            "\U0001f976": "@_@",  # @_@ Cold face
            "\U0001f974": "@_@",  # @_@ Woozy face
            "\U0001f635": "X_X",  # X_X Dizzy face
            "\U0001f92f": "O.O",  # O.O Exploding head
            "\U0001f920": ":D",  # :D Cowboy hat face
            "\U0001f973": ":D",  # :D Partying face
            "\U0001f913": "B)",  # B) Nerd face
            "\U0001f9d0": "B|",  # B| Face with monocle
            "\U0001f615": ":/",  # :/ Confused face
            "\U0001f61f": ":/",  # :/ Worried face
            "\U0001f641": ":(",  # :( Slightly frowning face
            "\U00002639": ":(",  # :(? Frowning face
            "\U0001f62e": "O_O",  # O_O Face with open mouth
            "\U0001f62f": "o_o",  # o_o Hushed face
            "\U0001f632": "O_O",  # O_O Astonished face
            "\U0001f633": "O.O",  # O.O Flushed face
            "\U0001f97a": ">_<",  # >_< Pleading face
            "\U0001f626": "D:",  # D: Frowning face with open mouth
            "\U0001f627": "D:",  # D: Anguished face
            "\U0001f628": "D:",  # D: Fearful face
            "\U0001f630": "D:",  # D: Anxious face with sweat
            "\U0001f625": ":'",  # :' Sad but relieved face
            "\U0001f622": ":'(",  # :'( Crying face
            "\U0001f62d": "T_T",  # T_T Loudly crying face
            "\U0001f631": "O_O",  # O_O Face screaming in fear
            "\U0001f616": ">_<",  # >_< Confounded face
            "\U0001f623": ">_<",  # >_< Persevering face
            "\U0001f613": "'^^",  # '^^ Downcast face with sweat
            "\U0001f629": "X(",  # X( Weary face
            "\U0001f62b": "X(",  # X( Tired face
            "\U0001f624": ">:(",  # >:( Face with steam from nose
            "\U0001f621": ">:(",  # >:( Pouting face
            "\U0001f92c": "#$@%!",  # #$@%! Face with symbols on mouth
            "\U0001f608": ">:)",  # >:) Smiling face with horns
            "\U0001f47f": ">:|",  # >:| Angry face with horns
            "\U0001f480": "X_X",  # X_X Skull
            "\U00002620": "X_X",  # X_X? Skull and crossbones
            "\U0001f4a9": "#2",  # #2 Pile of poo
            "\U0001f921": ":o)",  # :o) Clown face
            "\U0001f479": ">[",  # >[ Ogre
            "\U0001f47a": ">]",  # >] Goblin
            "\U0001f47b": "OoO",  # OoO Ghost
            "\U0001f47d": "o.O",  # o.O Alien
            "\U0001f47e": "0.O",  # 0.O Alien monster
            "\U0001f916": "[ROBOT]",  # [ROBOT] Robot
            "\U0001f63a": ":3",  # :3 Grinning cat
            "\U0001f638": ":D",  # :D Grinning cat with smiling eyes
            "\U0001f639": ":')",  # :') Cat with tears of joy
            "\U0001f63b": "<3",  # <3 Smiling cat with heart-eyes
            "\U0001f63c": ";3",  # ;3 Cat with wry smile
            "\U0001f63d": ":*",  # :* Kissing cat
            "\U0001f640": ":(",  # :(( Weary cat
            "\U0001f63f": ":'(",  # :'( Crying cat
            "\U0001f63e": ">:3",  # >:3 Pouting cat
        }

    def _apply_known_unicode_replacements(self, content: str) -> Tuple[str, int]:
        """
        Apply known Unicode character replacements from configuration.

        Args:
            content: Original content

        Returns:
            Tuple of (modified_content, replacement_count)
        """
        modified_content = content
        replacement_count = 0

        # Replace known unicode characters with specific replacements
        for unicode_char, replacement in self.config["unicode_replacements"].items():
            if unicode_char in modified_content:
                count = modified_content.count(unicode_char)
                modified_content = modified_content.replace(unicode_char, replacement)
                replacement_count += count

        return modified_content, replacement_count

    def _apply_emoji_replacements(self, content: str) -> Tuple[str, int]:
        """
        Apply emoji to ASCII replacements.

        Args:
            content: Content to process

        Returns:
            Tuple of (modified_content, replacement_count)
        """
        # Combine all emoji replacements
        emoji_replacements = {}
        emoji_replacements.update(self._get_emoji_replacements())
        emoji_replacements.update(self._get_emoticon_replacements())

        new_content = []
        replacement_count = 0

        for char in content:
            if ord(char) > 127:
                if char in emoji_replacements:
                    new_content.append(emoji_replacements[char])
                    replacement_count += 1
                else:
                    new_content.append(self._replace_unknown_unicode_char(char))
                    replacement_count += 1
            else:
                new_content.append(char)

        return "".join(new_content), replacement_count

    def _replace_unknown_unicode_char(self, char: str) -> str:
        """
        Replace unknown Unicode character with appropriate ASCII alternative.

        Args:
            char: Unicode character to replace

        Returns:
            ASCII replacement string
        """
        char_code = ord(char)

        if char_code in range(0x2190, 0x21FF):  # Arrows
            return "->"
        elif char_code in range(0x2022, 0x2023):  # Bullet
            return "*"
        elif char_code in range(0x00D7, 0x00D8):  # Multiplication
            return "x"
        elif char_code in range(0x00F7, 0x00F8):  # Division
            return "/"
        elif char_code >= 0x1F300:  # Other emojis and symbols
            return ""  # Remove unknown emojis
        else:
            return "?"  # Generic replacement for other unicode

    def _replace_unicode_chars(self, content: str) -> Tuple[str, int]:
        """
        Replace Unicode characters with ASCII alternatives.

        Args:
            content: Original content

        Returns:
            Tuple of (modified_content, replacement_count)
        """
        modified_content = content
        replacement_count = 0

        # First, replace known unicode characters with specific replacements
        for unicode_char, replacement in self.config["unicode_replacements"].items():
            if unicode_char in modified_content:
                count = modified_content.count(unicode_char)
                modified_content = modified_content.replace(unicode_char, replacement)
                replacement_count += count

        # Apply emoji replacements using extracted helper methods
        modified_content, emoji_count = self._apply_emoji_replacements(modified_content)
        replacement_count += emoji_count

        return modified_content, replacement_count

    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create backup of file.

        Args:
            file_path: Path to backup

        Returns:
            Path to backup file or None if failed
        """
        if not self.config["create_backups"]:
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create inert backup filename - insert timestamp after original extension
            backup_name = f"{file_path.name}.{timestamp}.backup"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            self.stats["backups_created"] += 1
            return backup_path

        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single file for Unicode cleanup.

        Args:
            file_path: Path to process

        Returns:
            Processing result dictionary
        """
        # Ensure file_path is a Path object
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        result: Dict[str, Any] = {
            "processed": False,
            "modified": False,
            "unicode_replaced": 0,
            "backup_path": None,
            "error": None,
        }

        if not self._should_process_file(file_path):
            result["error"] = "excluded"
            return result

        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            result["processed"] = True
            self.stats["files_processed"] += 1

            # Detect Unicode characters
            unicode_chars = self._detect_unicode_chars(original_content)
            if not unicode_chars:
                return result

            # Process Unicode characters based on mode
            if self.mode == "delete":
                modified_content, change_count = self._delete_unicode_chars(
                    original_content
                )
                result["unicode_deleted"] = change_count
                self.stats["unicode_characters_deleted"] += change_count
            else:
                # Replace mode
                modified_content, change_count = self._replace_unicode_chars(
                    original_content
                )
                result["unicode_replaced"] = change_count
                self.stats["unicode_characters_replaced"] += change_count

            if change_count > 0:
                # Create backup
                backup_path = self._create_backup(file_path)
                result["backup_path"] = str(backup_path) if backup_path else None

                # Write modified content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)

                result["modified"] = True
                self.stats["files_modified"] += 1

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error processing {file_path}: {e}")

        return result

    def process_directory(
        self, directory: Path, recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Process all files in a directory.

        Args:
            directory: Directory to process
            recursive: Whether to process subdirectories

        Returns:
            Processing summary
        """
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        logger.info(f"Processing directory: {directory}")

        pattern = "**/*" if recursive else "*"
        files_processed = 0
        files_modified = 0

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                result = self.process_file(file_path)
                if result["processed"]:
                    files_processed += 1
                    if result["modified"]:
                        files_modified += 1

        summary = {
            "directory": str(directory),
            "files_processed": files_processed,
            "files_modified": files_modified,
            "total_replacements": self.stats["unicode_characters_replaced"],
            "total_deletions": self.stats["unicode_characters_deleted"],
            "mode": self.mode,
        }

        logger.info(f"Directory processing complete: {summary}")
        return summary

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "unicode_characters_replaced": 0,
            "unicode_characters_deleted": 0,
            "backups_created": 0,
        }
