#!/bin/sh
#VirtIOBlk.jar为打包好的java可执行程序，$*为所传递的所有参数
#java -jar VirtioBlk.jar $*
java -jar "$(pwd)/lib/virtio_blk/VirtioBlk.jar" $*
