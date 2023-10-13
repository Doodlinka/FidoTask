# FidoTask
A parser for the NaUKMA schedules

### Specification
- Input: a folder with .tsv and .txt files in it
- Output: a .json with ALL of their data in this structure:
    - faculty
    - year
    - specialty
    - day of week
    - time (as string)
    - lessons
    - subject, teacher, group, weeks (as int list), location

### TODO: (maybe)
- a CLI asing for the input dir, output file and whether 
    you want to append to the output file
- consider passing tokens into the parser, not the fd
- store time as a time range? for /now and /next
- don't add empty dicts
- fix duplicate code
- map extensions to parsers instead of an elif tower
- output a database (sql or smth) instead of a json, to make it easy to search by any value, not just those that happened to be keys