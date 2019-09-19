[](https://github.com/NVIDIA/nvidia-docker/issues/534)
https://blog.sigsegowl.xyz/opengl-offscreen-software-rendering-on-a-server/
https://github.com/nigels-com/glew/issues/164
https://github.com/svenpilz/egl_offscreen_opengl
    sudo apt-get libopencv-dev
    sudo apt-get install libgles2-mesa-dev
    g++ egl.cpp -lGL -lEGL `pkg-config --cflags --libs opencv`

https://devblogs.nvidia.com/egl-eye-opengl-visualization-without-x-server/#disqus_thread