
# Load necessary library
library(dplyr)

# Get a list of all CSV files in the current directory
csv_files <- list.files(pattern = "\.csv$")

# Function to read a CSV file and validate its 'source_file' column
read_and_combine <- function(file) {
  # Read the CSV file
  df <- read.csv(file)
  
  # Ensure the 'source_file' column matches the filename (sanity check)
  stopifnot(all(df$source_file == tools::file_path_sans_ext(basename(file))))
  
  return(df)
}

# Read and combine all CSV files into a single dataframe
combined_data <- bind_rows(lapply(csv_files, read_and_combine))

# View the combined data
print(combined_data)
