def mirror(clear: str) -> str:
    def is_palindrome(s: str) -> bool:
        return s == s[::-1]
    half = len(clear) // 2
    half_rev = clear[:half][::-1] + clear[half:]
    if is_palindrome(clear) or is_palindrome(half_rev):
        return half_rev
    return clear[::-1]

if __name__ == "__main__":
    user_input = input("Enter a string to mirror: ")
    print(f"Mirrored output: {mirror(user_input)}")