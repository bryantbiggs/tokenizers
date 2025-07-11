import json
import pickle

import pytest

from tokenizers.pre_tokenizers import (
    BertPreTokenizer,
    ByteLevel,
    CharDelimiterSplit,
    Digits,
    FixedLength,
    Metaspace,
    PreTokenizer,
    Punctuation,
    Sequence,
    Split,
    UnicodeScripts,
    Whitespace,
    WhitespaceSplit,
)


class TestByteLevel:
    def test_instantiate(self):
        assert ByteLevel() is not None
        assert ByteLevel(add_prefix_space=True) is not None
        assert ByteLevel(add_prefix_space=False) is not None
        assert isinstance(ByteLevel(), PreTokenizer)
        assert isinstance(ByteLevel(), ByteLevel)
        assert isinstance(pickle.loads(pickle.dumps(ByteLevel())), ByteLevel)

    def test_has_alphabet(self):
        assert isinstance(ByteLevel.alphabet(), list)
        assert len(ByteLevel.alphabet()) == 256

    def test_can_modify(self):
        pretok = ByteLevel(add_prefix_space=False)

        assert pretok.add_prefix_space == False

        # Modify these
        pretok.add_prefix_space = True
        assert pretok.add_prefix_space == True

    def test_manual_reload(self):
        byte_level = ByteLevel()
        state = json.loads(byte_level.__getstate__())
        reloaded = ByteLevel(**state)
        assert isinstance(reloaded, ByteLevel)


class TestSplit:
    def test_instantiate(self):
        pre_tokenizer = Split(pattern=" ", behavior="removed")
        assert pre_tokenizer is not None
        assert isinstance(pre_tokenizer, PreTokenizer)
        assert isinstance(pre_tokenizer, Split)
        assert isinstance(pickle.loads(pickle.dumps(Split(" ", "removed"))), Split)

        # test with invert=True
        pre_tokenizer_with_invert = Split(pattern=" ", behavior="isolated", invert=True)
        assert pre_tokenizer_with_invert is not None
        assert isinstance(pre_tokenizer_with_invert, PreTokenizer)
        assert isinstance(pre_tokenizer_with_invert, Split)
        assert isinstance(pickle.loads(pickle.dumps(Split(" ", "removed", True))), Split)


class TestWhitespace:
    def test_instantiate(self):
        assert Whitespace() is not None
        assert isinstance(Whitespace(), PreTokenizer)
        assert isinstance(Whitespace(), Whitespace)
        assert isinstance(pickle.loads(pickle.dumps(Whitespace())), Whitespace)


class TestWhitespaceSplit:
    def test_instantiate(self):
        assert WhitespaceSplit() is not None
        assert isinstance(WhitespaceSplit(), PreTokenizer)
        assert isinstance(WhitespaceSplit(), WhitespaceSplit)
        assert isinstance(pickle.loads(pickle.dumps(WhitespaceSplit())), WhitespaceSplit)


class TestBertPreTokenizer:
    def test_instantiate(self):
        assert BertPreTokenizer() is not None
        assert isinstance(BertPreTokenizer(), PreTokenizer)
        assert isinstance(BertPreTokenizer(), BertPreTokenizer)
        assert isinstance(pickle.loads(pickle.dumps(BertPreTokenizer())), BertPreTokenizer)


class TestMetaspace:
    def test_instantiate(self):
        assert Metaspace() is not None
        assert Metaspace(replacement="-") is not None
        with pytest.raises(ValueError, match="expected a string of length 1"):
            Metaspace(replacement="")
        assert Metaspace(prepend_scheme="always") is not None
        assert isinstance(Metaspace(), PreTokenizer)
        assert isinstance(Metaspace(), Metaspace)
        assert isinstance(pickle.loads(pickle.dumps(Metaspace())), Metaspace)

    def test_can_modify(self):
        pretok = Metaspace(replacement="$", prepend_scheme="never")

        assert pretok.replacement == "$"
        assert pretok.prepend_scheme == "never"
        assert pretok.split == True

        # Modify these
        pretok.replacement = "%"
        assert pretok.replacement == "%"
        pretok.prepend_scheme = "first"
        assert pretok.prepend_scheme == "first"
        pretok.split = True
        assert pretok.split == True


class TestCharDelimiterSplit:
    def test_instantiate(self):
        assert CharDelimiterSplit("-") is not None
        with pytest.raises(ValueError, match="expected a string of length 1"):
            CharDelimiterSplit("")
        assert isinstance(CharDelimiterSplit(" "), PreTokenizer)
        assert isinstance(CharDelimiterSplit(" "), CharDelimiterSplit)
        assert isinstance(pickle.loads(pickle.dumps(CharDelimiterSplit("-"))), CharDelimiterSplit)

    def test_can_modify(self):
        pretok = CharDelimiterSplit("@")
        assert pretok.delimiter == "@"

        # Modify these
        pretok.delimiter = "!"
        assert pretok.delimiter == "!"


class TestPunctuation:
    def test_instantiate(self):
        assert Punctuation() is not None
        assert Punctuation("removed") is not None
        assert isinstance(Punctuation(), PreTokenizer)
        assert isinstance(Punctuation(), Punctuation)
        assert isinstance(pickle.loads(pickle.dumps(Punctuation())), Punctuation)


class TestSequence:
    def test_instantiate(self):
        assert Sequence([]) is not None
        assert isinstance(Sequence([]), PreTokenizer)
        assert isinstance(Sequence([]), Sequence)
        dumped = pickle.dumps(Sequence([]))
        assert isinstance(pickle.loads(dumped), Sequence)

    def test_bert_like(self):
        pre_tokenizer = Sequence([WhitespaceSplit(), Punctuation()])
        assert isinstance(Sequence([]), PreTokenizer)
        assert isinstance(Sequence([]), Sequence)
        assert isinstance(pickle.loads(pickle.dumps(pre_tokenizer)), Sequence)

        result = pre_tokenizer.pre_tokenize_str("Hey friend!     How are you?!?")
        assert result == [
            ("Hey", (0, 3)),
            ("friend", (4, 10)),
            ("!", (10, 11)),
            ("How", (16, 19)),
            ("are", (20, 23)),
            ("you", (24, 27)),
            ("?", (27, 28)),
            ("!", (28, 29)),
            ("?", (29, 30)),
        ]

    def test_set_item(self):
        pre_tokenizers = Sequence(
            [
                ByteLevel(),
                Split(pattern="/test/", behavior="removed"),
            ]
        )
        assert pre_tokenizers[0].__class__ == ByteLevel
        assert pre_tokenizers[1].__class__ == Split
        pre_tokenizers[1] = Metaspace()
        assert pre_tokenizers[1].__class__ == Metaspace
        with pytest.raises(IndexError):
            print(pre_tokenizers[2])

    def test_item_getters_and_setters(self):
        pre_tokenizers = Sequence(
            [
                ByteLevel(add_prefix_space=True, trim_offsets=True, use_regex=True),
                Split(pattern="/test/", behavior="removed", invert=False),
                Metaspace("a", "never", split=False),
                CharDelimiterSplit(delimiter=" "),
                Punctuation(behavior="removed"),
                Digits(individual_digits=True),
            ]
        )

        assert pre_tokenizers[0].__class__ == ByteLevel
        pre_tokenizers[0].add_prefix_space = False
        pre_tokenizers[0].trim_offsets = False
        pre_tokenizers[0].use_regex = False
        assert not pre_tokenizers[0].add_prefix_space
        assert not pre_tokenizers[0].trim_offsets
        assert not pre_tokenizers[0].use_regex

        assert pre_tokenizers[1].__class__ == Split
        with pytest.raises(Exception):
            pre_tokenizers[1].pattern = "/pattern/"
        pre_tokenizers[1].behavior = "isolated"
        pre_tokenizers[1].invert = True
        with pytest.raises(Exception):
            pre_tokenizers[1].pattern
        assert pre_tokenizers[1].behavior == "isolated"
        assert pre_tokenizers[1].invert

        assert pre_tokenizers[2].__class__ == Metaspace
        pre_tokenizers[2].replacement = " "
        pre_tokenizers[2].prepend_scheme = "always"
        pre_tokenizers[2].split = True
        assert pre_tokenizers[2].replacement == " "
        assert pre_tokenizers[2].prepend_scheme == "always"
        assert pre_tokenizers[2].split

        assert pre_tokenizers[3].__class__ == CharDelimiterSplit
        pre_tokenizers[3].delimiter = "_"
        assert pre_tokenizers[3].delimiter == "_"

        assert pre_tokenizers[4].__class__ == Punctuation
        pre_tokenizers[4].behavior = "isolated"
        assert pre_tokenizers[4].behavior == "isolated"

        assert pre_tokenizers[5].__class__ == Digits
        pre_tokenizers[5].individual_digits = False
        assert not pre_tokenizers[5].individual_digits


class TestDigits:
    def test_instantiate(self):
        assert Digits() is not None
        assert isinstance(Digits(), PreTokenizer)
        assert isinstance(Digits(), Digits)
        assert isinstance(Digits(True), Digits)
        assert isinstance(Digits(False), Digits)
        assert isinstance(pickle.loads(pickle.dumps(Digits())), Digits)

    def test_can_modify(self):
        pretok = Digits(individual_digits=False)
        assert pretok.individual_digits == False

        # Modify these
        pretok.individual_digits = True
        assert pretok.individual_digits == True


class TestFixedLength:
    def test_instantiate(self):
        assert FixedLength() is not None
        assert isinstance(FixedLength(), PreTokenizer)
        assert isinstance(FixedLength(), FixedLength)
        assert isinstance(pickle.loads(pickle.dumps(FixedLength())), FixedLength)

    def test_pre_tokenize_str(self):
        pretok = FixedLength(length=5)
        assert pretok.length == 5
        assert pretok.pre_tokenize_str("ATCCTGGTACTG") == [
            ("ATCCT", (0, 5)),
            ("GGTAC", (5, 10)),
            ("TG", (10, 12)),
        ]

        pretok.length = 10
        assert pretok.length == 10
        assert pretok.pre_tokenize_str("ATCCTGGTACTG") == [
            ("ATCCTGGTAC", (0, 10)),
            ("TG", (10, 12)),
        ]


class TestUnicodeScripts:
    def test_instantiate(self):
        assert UnicodeScripts() is not None
        assert isinstance(UnicodeScripts(), PreTokenizer)
        assert isinstance(UnicodeScripts(), UnicodeScripts)
        assert isinstance(pickle.loads(pickle.dumps(UnicodeScripts())), UnicodeScripts)


class TestCustomPreTokenizer:
    class BadCustomPretok:
        def pre_tokenize(self, pretok, wrong):
            # This method does not have the right signature: it takes one too many arg
            pass

    class GoodCustomPretok:
        def split(self, n, normalized):
            #  Here we just test that we can return a List[NormalizedString], it
            # does not really make sense to return twice the same otherwise
            return [normalized, normalized]

        def pre_tokenize(self, pretok):
            pretok.split(self.split)

    def test_instantiate(self):
        bad = PreTokenizer.custom(TestCustomPreTokenizer.BadCustomPretok())
        good = PreTokenizer.custom(TestCustomPreTokenizer.GoodCustomPretok())

        assert isinstance(bad, PreTokenizer)
        assert isinstance(good, PreTokenizer)
        with pytest.raises(Exception, match="TypeError:.*pre_tokenize()"):
            bad.pre_tokenize_str("Hey there!")
        assert good.pre_tokenize_str("Hey there!") == [
            ("Hey there!", (0, 10)),
            ("Hey there!", (0, 10)),
        ]

    def test_camel_case(self):
        class CamelCasePretok:
            def get_state(self, c):
                if c.islower():
                    return "lower"
                elif c.isupper():
                    return "upper"
                elif c.isdigit():
                    return "digit"
                else:
                    return "rest"

            def split(self, n, normalized):
                i = 0
                # states = {"any", "lower", "upper", "digit", "rest"}
                state = "any"
                pieces = []
                for j, c in enumerate(normalized.normalized):
                    c_state = self.get_state(c)
                    if state == "any":
                        state = c_state
                    if state != "rest" and state == c_state:
                        pass
                    elif state == "upper" and c_state == "lower":
                        pass
                    else:
                        pieces.append(normalized[i:j])
                        i = j
                    state = c_state
                pieces.append(normalized[i:])
                return pieces

            def pre_tokenize(self, pretok):
                pretok.split(self.split)

        camel = PreTokenizer.custom(CamelCasePretok())

        assert camel.pre_tokenize_str("HeyThere!?-ThisIsLife") == [
            ("Hey", (0, 3)),
            ("There", (3, 8)),
            ("!", (8, 9)),
            ("?", (9, 10)),
            ("-", (10, 11)),
            ("This", (11, 15)),
            ("Is", (15, 17)),
            ("Life", (17, 21)),
        ]
