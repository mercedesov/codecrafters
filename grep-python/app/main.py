
#!/usr/bin/env python3
import sys

def tokenize(pattern):
    tokens = []
    i = 0
    while i < len(pattern):
        if pattern[i] == "\\":
            tokens.append(pattern[i:i+2])
            i += 2
        elif pattern[i] in "^$":
            tokens.append(pattern[i])
            i += 1
        elif pattern[i] == "[":
            j = i
            while j < len(pattern) and pattern[j] != "]":
                j += 1
            tokens.append(pattern[i:j+1])
            i = j + 1
        elif i + 1 < len(pattern) and pattern[i+1] == "+":
            tokens.append(pattern[i] + "+")
            i += 2
        else:
            tokens.append(pattern[i])
            i += 1
    return tokens

def match_token(token, c):
    if token == "\\d":
        return c.isdigit()
    elif token == "\\w":
        return c.isalnum() or c == "_"
    elif token.startswith("[^") and token.endswith("]"):
        return c not in set(token[2:-1])
    elif token.startswith("[") and token.endswith("]"):
        return c in set(token[1:-1])
    elif len(token) == 2 and token[1] == "+":
        raise RuntimeError("Quantifier should be expanded in matcher")
    else:
        return c == token

def match_from(input_line, tokens, pos, ti):
    n = len(input_line)
    m = len(tokens)
    while ti < m:
        token = tokens[ti]
        if token == "$":
            return pos == n
        elif token == "^":
            if pos != 0:
                return False
            ti += 1
            continue
        elif len(token) == 2 and token[1] == "+":
            base = token[0]
            if pos >= n or not match_token(base, input_line[pos]):
                return False
            pos += 1
            while pos < n and match_token(base, input_line[pos]):
                pos += 1
            ti += 1
            continue
        elif token.startswith("(") and token.endswith(")"):
            group_pat = token[1:-1]
            if pos + len(group_pat) <= n and input_line[pos:pos+len(group_pat)] == group_pat:
                ti += 1
                pos += len(group_pat)
            else:
                return False
        elif token.startswith("\\") and token[1].isdigit():
            ref_num = int(token[1])
            captured_text = captures[ref_num - 1] if ref_num <= len(captures) else ""
            if input_line.startswith(captured_text, pos):
                pos += len(captured_text)
                ti += 1
            else:
                return False
        else:
            if pos >= n or not match_token(token, input_line[pos]):
                return False
            pos += 1
            ti += 1
    return pos == n or (m > 0 and tokens[-1] == "$")

def match_pattern(input_line, pattern):
    global captures
    captures = []
    anchored_start = pattern.startswith("^")
    anchored_end = pattern.endswith("$")
    tokens = tokenize(pattern[1:] if anchored_start else pattern)
    if anchored_start:
        return match_from(input_line, tokens, 0, 0)
    else:
        for start in range(len(input_line)):
            if match_from(input_line[start:], tokens, 0, 0):
                return True
        return False

def main():
    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)
    pattern = sys.argv[2]
    input_line = sys.stdin.read().rstrip("\n")
    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
