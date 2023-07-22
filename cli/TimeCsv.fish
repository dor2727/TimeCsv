
complete -c "TimeCsv" --short-option fdmyv

complete -c "TimeCsv" --require-parameter            --long-option file
complete -c "TimeCsv" --require-parameter            --long-option folder
complete -c "TimeCsv" --require-parameter --no-files --long-option days-back
complete -c "TimeCsv" --require-parameter --no-files --long-option months-back
complete -c "TimeCsv" --require-parameter --no-files --long-option month
complete -c "TimeCsv" --require-parameter --no-files --long-option year
complete -c "TimeCsv"                     --no-files --long-option all-time
complete -c "TimeCsv"                     --no-files --long-option time-use-and
complete -c "TimeCsv"                     --no-files --long-option search-use-or
complete -c "TimeCsv" --require-parameter --no-files --long-option max-hirarchy
complete -c "TimeCsv"                     --no-files --long-option max-main
complete -c "TimeCsv"                     --no-files --long-option max-main-group
complete -c "TimeCsv" --require-parameter --no-files --long-option max-sub-group
complete -c "TimeCsv"                     --no-files --long-option max-description
complete -c "TimeCsv"                     --no-files --long-option max-extra-details-keys
complete -c "TimeCsv"                     --no-files --long-option max-extra-details-values
complete -c "TimeCsv" --require-parameter --no-files --long-option sort-method
complete -c "TimeCsv"                     --no-files --long-option alphabetical
complete -c "TimeCsv"                     --no-files --long-option abc
complete -c "TimeCsv"                     --no-files --long-option total-time
complete -c "TimeCsv"                     --no-files --long-option time
complete -c "TimeCsv"                     --no-files --long-option pie
complete -c "TimeCsv"                     --no-files --long-option debug
complete -c "TimeCsv"                     --no-files --long-option verbose
