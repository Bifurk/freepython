# def is_printable(char_code):
#     return 32 <= char_code <= 126 or 160 <= char_code <= 255

# def format_char(char_code):
#     if is_printable(char_code):
#         return f"{char_code}:{chr(char_code)}"
#     else:
#         return f"{char_code}:"

# # Define the number of columns you want to display
# num_columns = 4

# # Define the range of extended ASCII characters
# ascii_start = 0
# ascii_end = 256

# # Calculate the number of rows
# num_rows = -(-ascii_end // num_columns)  # equivalent to ceil(ascii_end / num_columns)

# # Iterate over the range of extended ASCII characters and print them in columns
# for i in range(num_rows):
#     for j in range(num_columns):
#         index = i + j * num_rows
#         if index < ascii_end:
#             formatted_char = format_char(index)
#             print(formatted_char.ljust(8), end="\t")
#     print()



def format_char(char_code):
    return f"{char_code}:{chr(char_code)}"

num_columns = 4
ascii_start = 0
ascii_end = 256
num_rows = -(-ascii_end // num_columns)

for i in range(num_rows):
    for j in range(num_columns):
        index = i + j * num_rows
        if index < ascii_end:
            formatted_char = format_char(index)
            print(formatted_char.ljust(9), end=" ")
    print()

# sloupce nejsou správně zarovnány kvůli netisknutelných znaků. Vzhledem k tomu, že konzola nemusí netisknutelné znaky zpracovávat správně, je obtížné zachovat zarovnání sloupců při tisku.
# paráda, že jsi to zkusil, ale v tomhle případě bych to nechal na jednom řádku, protože to je jenom jedna funkce, která se volá v cyklu.


