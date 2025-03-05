define copy-file
	$(eval $@_SRC := $(1))
	$(eval $@_DST := $(2))
	$(eval $@_LOG_PREFIX := $(3))
	$(eval $@_FORCE := $(or $(4), false))

	if [ "$($@_FORCE)" = "false" ] && [ -f "$($@_DST)" ]; then \
		echo "$($@_LOG_PREFIX) $($@_DST) already exists, not overwriting"; \
	else \
		echo "$($@_LOG_PREFIX) Copying $($@_SRC) to $($@_DST)"; \
		mkdir -p $(dir $($@_DST)) && cp $($@_SRC) $($@_DST); \
	fi
endef

define copy-dir
	$(eval $@_SRC := $(1))
	$(eval $@_DST := $(2))
	$(eval $@_LOG_PREFIX := $(3))
	$(eval $@_FORCE := $(or $(4), false))

	if [ "$($@_FORCE)" = "false" ] && [ -d "$($@_DST)" ]; then \
		echo "$($@_LOG_PREFIX) $($@_DST) already exists, not overwriting"; \
	else \
		echo "$($@_LOG_PREFIX) Copying $($@_SRC) to $($@_DST)"; \
		mkdir -p $(dir $($@_DST)) && cp -rT $($@_SRC) $($@_DST); \
	fi
endef
