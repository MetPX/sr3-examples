
script_to_run=$1

if [ ! -f "${script_to_run}" ]; then
  script_to_run=/bin/bash

  #echo "please supply a script to run"
  #exit 4
fi

shim_location="/usr/lib"

if [ ! "`ls ${shim_location}/libsr3shim.so*`" ] ; then
    echo "no shim library installed at ${shim_location}"
    exit 1
fi

shim_version="`ls ${shim_location}/libsr3shim.so.3.*|sed \"s+${shim_location}/libsr3shim\.so\.++\"`"

if [ ! "${shim_version}"  ]; then
   echo "no shim library found" 
   exit 2
fi

shim_short_config="mirror"
shim_config="${HOME}/.config/sr3/cpost/${shim_short_config}.conf"

if [ ! -f "${shim_config}" ]; then
    echo "no configuration found"
    exit 3
fi
#echo config=${shim_config}
#echo short_config=${shim_short_config}
#echo location=${shim_location}
#echo version=${shim_version}

#export SR_SHIMDEBUG=99

#echo export SR_SHIM_CONFIG=${shim_config}
#echo export SR_POST_CONFIG=${shim_config}
export SR_POST_CONFIG=${shim_short_config}
echo  using: SR_POST_CONFIG=${shim_short_config} LD_PRELOAD="${shim_location}/libsr3shim.so.${shim_version}"
export LD_PRELOAD="${shim_location}/libsr3shim.so.${shim_version}"

echo launching: exec ${script_to_run}
exec ${script_to_run}
