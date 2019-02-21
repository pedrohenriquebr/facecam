prefix := $(PWD)
exec_prefix := $(prefix)
bindir := $(exec_prefix)/bin
datarootdir := $(exec_prefix)/facecam_data
datadir := $(datarootdir)
tmp_img := $(datadir)/img.jpg

include web-face-recognition/.env

define run_recognition_server
	cd web-face-recognition && \
	$(MAKE) clean && \
    $(MAKE) run-dev && \
    $(MAKE) train && \
    $(MAKE) clean && \
    $(MAKE) -e SCALE=$(1) run
endef

define stop_recognition_server 
	cd web-face-recognition && $(MAKE) stop
endef

.PHONY: prepare start-server stop-server start stop uninstall

prepare: requirements.txt
	sudo mkdir -p $(datadir) && \
	sudo chown -R $(USER):$(USER) $(datarootdir) && \
	sudo chmod -R 0775 $(datarootdir) && \
	pip3 install -r  $< 

start-server: web-face-recognition/
	$(call run_recognition_server,1)

stop-server: web-face-recognition/
	$(call stop_recognition_server)

start:
	echo "FACECAM_DATA_DIR=${datadir}" > src/.env;\
	echo "RECOGNITION_HOST=${VIRTUAL_HOST}" >> src/.env
	echo "TMP_IMG=${tmp_img}" >> src/.env
	cd src;\
	python3 facecam.py start

stop:
	cd src;\
	python3 facecam.py stop

uninstall:
	rm -rf $(datadir)