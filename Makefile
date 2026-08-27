check-images:
	@bash check-image-sizes.sh

build: check-images
	LANG="en_US.UTF-8" LC_ALL="en_US.UTF-8" RUBYOPT="-r./_plugins/ruby3_taint_compat" bundle exec jekyll build

upload:
	rsync -av --delete  _site/ cproof@cproof.uvic.ca:Sites --exclude=gliderdata

cp: check-images
	rsync -av --delete  _site/ /home/cproof/public_html --exclude=gliderdata
