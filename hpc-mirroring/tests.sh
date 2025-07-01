

reallyme=`realpath $0`
mirrundir=`dirname ${reallyme}`

printf "mirrundir=${mirrundir}\n"

cd ~/fakeplace

mkdir test1
cd test1
   git clone https://github.com/MetPX/sarrac metpx-sr3c
   #cd metpx-sr3c
   #   ./shim_copy_post2.sh
   #cd ..
cd ..

exit

mkdir test2
cd test2
   #echo git clone  https://github.com/torvalds/linux 
cd ..

sec=45
printf "wait copies to complete, around 45 seconds"
sleep ${sec}
