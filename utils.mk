define copy-file
	@{ \
		$(eval $@_SRC := $(1)) \
		$(eval $@_DST := $(2)) \
		$(eval $@_LOG_PREFIX := $(3)) \
		$(eval $@_FORCE := $(or $(4), false)) \
 		\
		if [ "$($@_FORCE)" = "false" ] && [ -f "$($@_DST)" ]; then \
			echo "$($@_LOG_PREFIX) $($@_DST) already exists, not overwriting"; \
		else \
			echo "$($@_LOG_PREFIX) Copying $($@_SRC) to $($@_DST)"; \
			mkdir -p $(dir $($@_DST)) && cp $($@_SRC) $($@_DST); \
		fi; \
	}
endef

define copy-dir
	@{ \
		$(eval $@_SRC := $(1)) \
		$(eval $@_DST := $(2)) \
		$(eval $@_LOG_PREFIX := $(3)) \
		$(eval $@_FORCE := $(or $(4), false)) \
		\
		if [ -d "$($@_DST)" ]; then \
			if [ "$($@_FORCE)" = "true" ]; then \
				echo "$($@_LOG_PREFIX) Removing $($@_DST)"; \
				rm -r $($@_DST); \
			else \
				echo "$($@_LOG_PREFIX) $($@_DST) already exists, not overwriting"; \
				exit 0; \
			fi; \
		fi; \
		\
		echo "$($@_LOG_PREFIX) Copying $($@_SRC) to $($@_DST)"; \
		cp -r $($@_SRC) $($@_DST); \
	}
endef
