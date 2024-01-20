# Desc: Count the number of words in all markdown files in the docs directory
# Usage: ./wordcount.sh
# Outputs: The number of words in each file and the total number of words in all files
find docs -name \*.md -type f -exec wc -w {} +
