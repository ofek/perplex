#!/usr/bin/with-contenv bash

cd /config
tar -czf /tmp/pms_config-latest.tar.gz Library --exclude=*/Cache/* --exclude=*/Caches/* "--exclude=*/Crash Reports/*"
gsutil cp /tmp/pms_config-latest.tar.gz gs://$BUCKET_METADATA/pms_config-latest.tar.gz
gsutil cp gs://$BUCKET_METADATA/pms_config-latest.tar.gz gs://$BUCKET_METADATA/Snapshots/pms_config-`date +\%Y-\%m-\%d`.tar.gz
