
# Load necessary library
library(dplyr)

# Get a list of all CSV files in the current directory
csv_files <- list.files(pattern = "\.csv$")
print(csv_files)
# Function to read a CSV file and validate its 'id' column
read_and_combine <- function(file) {
  # Read the CSV file
  df <- read.csv(file)
  names(df)
  # Ensure the 'id' column matches the filename (sanity check)
  stopifnot(all(df$id == tools::file_path_sans_ext(basename(file))))
  
  return(df)
}

# Read and combine all CSV files into a single dataframe
combined_data <- bind_rows(lapply(csv_files, read_and_combine))

# View the combined data
print(combined_data)
