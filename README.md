# FidoTask

Fido's ennrance test - a parser for the NaUKMA schedules.

## Usage

Requires Python 3.10+ (or 3.x, idk) to run.
Input: a folder with .tsv and .txt files in it
Output: a .json with ALL of their data in this structure:

- faculty
- year
- specialty
- day of week
- time (as string)
- lessons
- subject, teacher, group, weeks (as list of ints), location

Both should be in the script's folder.

## Resources

- Python with the following libraries:
  - os for working with files
  - re to cut the input into tokens and check for time
  - json to generate the output file
- Docs, google, stackoverflow etc
- Duct tape, crutches, prayers

## TODO if I had the time and it was actually needed

- a CLI asking for the input dir, output file and whether you want to edit or overwrite the output file
- pass tokens into the TSV parser, not the fd, for consistency
- store time as a time range for /now and /next
- don't add empty values
- fix duplicate code
- map extensions to parsers instead of an elif tower
- output a database (sql or smth) instead of a json, to make it easy to search by any value, not just those that happened to be keys
- change tokenize to only read portons of the file at a time, piecing together any tokens that got split
- unhardcode the lesson/day order (LESSONORDER exists, but is barely used)
