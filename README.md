# FidoTask

Fido's entrance test - a parser for the NaUKMA schedules.

## Development history

I decided to export the inputs into .tsv and .txt, since these formats were the simplest and presumably the easiest to work with. TSV has more consistent formatting, so that's where I started, figuring out the file's structure on the way.
After finishing .tsv parsing and output generating, I started adapting the code to the .txt. However, I ran into a problem: this format separates different cells with newlines, which were contained in the cells themselves. The crutches weren't enough to circumvent that, so I decided, a day before the deadline, to read from the .doc itself. Luckily, the inner structure was simple (though bloated), and I've parsed .xml before. With all the code for converting the schedule's data already written, getting the second half of the task to work didn't take long.
In conclusion, this seems to work well, though I haven't tested it thoroughly and it can be improved.

## Preprocessing required

Install Python 3.10+ (or 3.x, idk) to run the script with.
For any .xlsx file, open it in an Excel-like program, export it as a .tsv, and put it in the script's "input" folder.
For any .doc file, open it in a Word-like program, save it as a .docx, unarchive it like a regular zip. Find the resulting folder, find "document.xml" in the "word" subfolder, and put the xml in the script's "input" folder.

## Output

A .json with ALL of the input files' data in this structure:

- faculty
- year
- specialty
- day of week
- time (as string)
- lessons
- subject, teacher, group, weeks (as list of ints), location

## Resources used

- Python with the following libraries:
  - os for working with files
  - re to check for time
  - json to generate the output file
  - xml.etree to read XML files
- Docs, google, stackoverflow etc
- Duct tape, crutches, prayers

## TODO if I had the time and it was actually needed

- a CLI asking for the input dir, output file and whether you want to edit or overwrite the output file
- store time as a time range for /now and /next
- don't add empty values
- fix duplicate code
- map extensions to parsers instead of an elif tower
- output a database (sql or something) instead of a json, to make it easy to search by any value, not just those that happened to be keys
- unhardcode the lesson/day order (LESSONORDER exists, but is barely used)
- use XML parsing for the xlsx tables too
