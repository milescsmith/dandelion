#! /bin/sh

# fix pathing
echo "export GERMLINE=/share/database/germlines/" | tee -a $SINGULARITY_ENVIRONMENT
echo "export IGDATA=/share/database/igblast/" | tee -a $SINGULARITY_ENVIRONMENT
echo "export BLASTDB=/share/database/blast/" | tee -a $SINGULARITY_ENVIRONMENT
echo "LANG=en_US.UTF-8" | tee -a $SINGULARITY_ENVIRONMENT
# chmod +x /share/dandelion_preprocess.py
# chmod +x /share/changeo_clonotypes.py
# install dependencies
# Get igblast
URL="https://ftp.ncbi.nih.gov/blast/executables/igblast/release/LATEST/"
latest_version=$(curl -s $URL | grep -oE 'igblast-[0-9]+\.[0-9]+\.[0-9]+' | head -1 | awk -F'-' '{print $2}')
mkdir /share/ncbi-igblast
curl -L "ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/LATEST/ncbi-igblast-$latest_version-x64-linux.tar.gz" | \
    tar -xzvf - -C /share/ncbi-igblast --strip-components 1
echo "export PATH=/share/ncbi-igblast/bin:$PATH" >/etc/profile.d/igblast.sh
echo "export IGBLAST_VERSION=$latest_version" >>/etc/profile.d/igblast.sh
chmod +x /etc/profile.d/igblast.sh
