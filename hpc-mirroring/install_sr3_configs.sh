
mkdir -p ~/.config/sr3/cpost ~/.config/sr3/winnow ~/.config/sr3/subscribe ~/.config/sr3/plugins

if [ -d config -a -d config/sr3 ]; then

    for c in cpost sarra shovel winnow; do
	cd config/sr3/${c}
	for cfg in *.inc *.conf ; do
	    if [ ! -f ~/.config/sr3/${c}/${cfg} ]; then
                cp ${cfg} ~/.config/sr3/${c}
	    fi
	done
	cd ../../../
    done

    cd config/sr3/plugins
    for p in *.py; do
	cp ${p} ~/.config/sr3/plugins
    done
    cd ../../../

    if [ ! -f ~/.config/sr3/default.conf ]; then
        cp config/sr3/default.conf ~/.config/sr3
    fi

fi
