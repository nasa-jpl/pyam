ifdef YAM_ROOT
	yam_root_defined="YAM_ROOT is defined"
else
	yam_root_defined="YAM_ROOT is not defined"
endif

root:
	rm -f root
	echo $(yam_root_defined) >> root

all: root
	rm -f all
	echo $(MODULES) >> all

clean:
	rm -f clean
	echo $(MODULES) >> clean

mklinks:
	rm -f mklinks
	echo $(MODULES) "release_directory=$(YAM_VERSIONS) site_name=$(YAM_SITE)" >> mklinks

rmlinks:
	rm -f rmlinks
	echo $(MODULES) >> rmlinks

rshtest:
	@echo SUCCESS

alltgt-all:
	rm -f alltgt-all
	echo $(MODULES) >> alltgt-all

alltgt-clean:
	rm -f alltgt-clean
	echo $(MODULES) >> alltgt-clean

alltgt-mklinks:
	rm -f alltgt-mklinks
	echo $(MODULES) "release_directory=$(YAM_VERSIONS) site_name=$(YAM_SITE)" >> alltgt-mklinks

alltgt-rmlinks:
	rm -f alltgt-rmlinks
	echo $(MODULES) >> alltgt-rmlinks
