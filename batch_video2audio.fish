#!/usr/bin/env fish

set -l ARGS (getopt -o i:o:f: -l input_dir:,output_dir:,output_format: -- $argv)

if test $status -ne 0
    echo "Failed to parse arguments"
    exit 1
end

eval set -- argv $ARGS

while test (count $argv) -gt 0
    switch $argv[1]
        case -i --input_dir
            set input_dir $argv[2]
            set argv $argv[3..-1]
        case -o --output_dir
            set output_dir $argv[2]
            set argv $argv[3..-1]
        case -f --output_format
            set output_format $argv[2]
            set argv $argv[3..-1]
        case --
            set argv $argv[2..-1]
            break
        case '*'
            echo "Unknown option: $argv[1]"
            exit 1
    end
end

switch $output_format
    case mp3
        set out_format libmp3lame
    case '*'
        echo "Unknown output format: $output_format"
        exit 1
end

for in_file in (find $input_dir -type f)
    echo "Processing: $in_file ================================================"
    set relative_path (string replace -r "^$input_dir/" '' -- $in_file)
    set out_dir (dirname $output_dir/$relative_path)
    set out_file (string replace -r '\.[^\.]+$' '' -- $output_dir/$relative_path)
    mkdir -p $out_dir
    ffmpeg -i $in_file -map 0:a -c:a $out_format "$out_file.$output_format" -y
end
