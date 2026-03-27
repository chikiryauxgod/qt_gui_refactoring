#!/bin/sh


ps h -p $$ # show info about proccess for current PID
printf \\U0001f4a9\\r\\n | hexdump
base_v=v0.0.
# commit amd push to git
git add *
echo "Enter commit msg and press [ENTER]: "
read msg
git commit -a -m "$msg"
echo "..and fix some \xf0\x9f\x92\xa9"
git pull && git push
ver_num=$(cat version.txt | tail -1)
echo $((ver_num+1)) >> version.txt
git add version.txt && git commit -m "fix version $ver_num"
git tag "$base_v"$((ver_num+1))
git push --tags
echo "That's \xf0\x9f\xa4\x98!"
echo "Let's drink some vodka with \xf0\x9f\x8d\xba!"
