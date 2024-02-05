%global oname MeshLab
%global name %(echo %oname | tr [:upper:] [:lower:])

%global bundled_libE57Format_version	2.3.0
%global bundled_libigl_version			2.4.0
%global bundled_OpenCTM_version			1.0.3
%global bundled_StructureSynth_version	1.5.1
%global bundled_tinygltf_version		2.6.3
%global bundled_u3d_version				1.5.1

Summary:	An open source system for processing and editing 3D triangular meshes
Name:		meshlab
Version:	2023.12
Release:	1
Group:		Graphics
# Bundled e57 is Boost-licensed
# bundled glew is BSD-3-Clause
# bundled picojson is BSD-2-Clause
License:	GPLv2+ and BSD-2-Clause and BSD-3-Clause and Public Domain and ASL 2.0 and BSL-1.0
URL:		https://github.com/cnr-isti-vclab/meshlab
Source0:	https://github.com/cnr-isti-vclab/meshlab/archive/MeshLab-%{version}/%{name}-%{version}.tar.gz
# FIXME: actually can't be build as a indipendent library
Source1:	https://github.com/cnr-isti-vclab/vcglib/archive/%{version}/vcglib-%{version}.tar.gz
# External projects are no more bundled into the archive
#   libE57Format
#   FIXME: consider packaging it separately
Source10:	https://github.com/asmaloney/libE57Format/archive/refs/tags/v%{bundled_libE57Format_version}/libE57Format-%{bundled_libE57Format_version}.zip
#   libigl
#   FIXME: consider packaging it separately
Source11:	https://github.com/libigl/libigl/archive/refs/tags/v%{bundled_libigl_version}/libigl-%{bundled_libigl_version}.zip
#   nexsus
#   FIXME: consider packaging it separately
Source12:	https://www.meshlab.net/data/libs/nexus-master.zip
#   corto
#   FIXME: consider packaging it separately
Source13:	https://www.meshlab.net/data/libs/corto-master.zip
#   nexsus
#   FIXME: consider packaging it separately (but no more mantained)
Source14:	https://www.meshlab.net/data/libs/OpenCTM-%{bundled_OpenCTM_version}-src.zip
#   nexsus (Meshlab's fork of StructureSynth
Source15:	https://github.com/alemuntoni/StructureSynth/archive/refs/tags/%{bundled_StructureSynth_version}/StructureSynth-%{bundled_StructureSynth_version}.zip
#   tinygltf 
#   FIXME: meshlar requirees an old version
Source16:	https://github.com/syoyo/tinygltf/archive/refs/tags/v%{bundled_tinygltf_version}/tinygltf-%{bundled_tinygltf_version}.zip
#   u3d
#   FIXME: consider packaging it separately
Source17:	https://www.meshlab.net/data/libs/u3d-%{bundled_u3d_version}.zip

Patch0:		fix_clang16.patch
Patch1:		meshlab-2023.12-fix_cmake_install_path.patch
Patch2:		meshlab-2023.12-corto-cstdint.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	boost-devel
BuildRequires:	cmake(cgal)
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(eigen3)
BuildRequires:	pkgconfig(glew)
BuildRequires: 	pkgconfig(glu)
BuildRequires: 	pkgconfig(gmp)
BuildRequires:	pkgconfig(levmar)
BuildRequires:	pkgconfig(lib3ds)
BuildRequires:	pkgconfig(libexif)
BuildRequires:	pkgconfig(muparser)
BuildRequires:	pkgconfig(xerces-c)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	qhull-devel
BuildRequires:	qt5-qtbase-devel
#BuildRequires:	qt5-qtdeclarative
#BuildRequires:	qt5-qtxmlpatterns
#BuildRequires:	qt5-qtscript
# (unpackaged)
BuildRequires:	embree-devel

%description
MeshLab is an open source, portable, and extensible system for the processing
and editing of unstructured large 3D triangular meshes. It is aimed to help
the processing of the typical not-so-small unstructured models arising in 3D
scanning, providing a set of tools for editing, cleaning, healing, inspecting,
rendering and converting this kind of meshes.

MeshLab is mostly based on the open source C++ mesh processing library VCGlib
developed at the Visual Computing Lab of ISTI - CNR. VCG can be used as a
stand-alone large-scale automated mesh processing pipeline, while MeshLab
makes it easy to experiment with its algorithms interactively.

%files
%license LICENSE.txt
%license src/external/u3d/COPYING
%license distrib/shaders/3Dlabs-license.txt
%license distrib/shaders/LightworkDesign-license.txt
#license unsupported/plugins_experimental/filter_segmentation/license.txt
#license unsupported/plugins_unsupported/filter_poisson/license.txt
%doc README.md
%doc docs/readme.txt
%doc docs/privacy.txt
%{_bindir}/%{name}*
%{_libdir}/%{name}/
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png
%{_datadir}/pixmaps/%{name}.xpm

#---------------------------------------------------------------------------

%prep
#autosetup -p1 -n %{name}-%{oname}-%{version} -a 10
%setup -q -n meshlab-MeshLab-%{version} -a 1
%patch -P 1 -p1 -b .libdirfix

# use vcglib from source
rm -fr src/vcglib
mv vcglib-%{version} src/vcglib

# fix plugin path
sed -i -e 's|"lib"|"%{_lib}"|g' src/common/globals.cpp

# add external sources
pushd src/external
mkdir -p downloads
cd downloads
unzip %{SOURCE10}
unzip %{SOURCE11}
unzip %{SOURCE12}
unzip %{SOURCE14}
unzip %{SOURCE15}
unzip %{SOURCE16}
unzip %{SOURCE17}
pushd nexus-master/src
rm -rf corto
unzip %{SOURCE13}
mv corto-master corto
popd
popd

# These patches need to apply after we build the bundled tree
#%patch -P 3 -p1 -b .e57-gcc13
%patch -P 2 -p1 -b .cstdint

	
# remove some bundles
	
%if 0
rm -rf src/external/glew*
rm -rf src/external/qhull*
#rm -rf src/external/levmar*
rm -rf src/external/lib3ds*
rm -rf src/external/muparser*
%endif

# plugin path
sed -i -e 's|"lib"|"%{_lib}"|g' src/common/globals.cpp

%build
%global cpp_std c++17
#export CXXFLAGS=`echo %{optflags} -std=c++14 -fopenmp -DSYSTEM_QHULL -I/usr/include/libqhull`

export CMAKE_BUILD_DIR=src/build
#global _vpath_srcdir src
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_BOOST:BOOL=OFF \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_CGAL:BOOL=OFF \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_LIBE57:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_EMBREE:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_LEVMAR:BOOL=OFF \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_LIB3DS:BOOL=OFF \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_LIBIGL:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_MUPARSER:BOOL=OFF \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_NEXUS:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_OPENCTM:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_STRUCTURE_SYNTH:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_TINYGLTF:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_U3D:BOOL=ON \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_XERCES:BOOL=OFF \
#	-DMESHLAB_ALLOW_DOWNLOAD_SOURCE_QHULL:BOOL=OFF \
#	-DMESHLAB_ALLOW_BUNDLED_SOURCE_EASYEXIF:BOOL=ON \
#	-DMESHLAB_ALLOW_BUNDLED_SOURCE_GLEW:BOOL=OFF \
#	-DMESHLAB_ALLOW_BUNDLED_NEWUOA:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_BOOST:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_CGAL:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_EMBREE:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_GLEW:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_LIB3DS_BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_MUPARSER:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_OPENCTM:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_QHULL:BOOL=ON \
#	-DMESHLAB_ALLOW_SYSTEM_XERCES:BOOL=ON \
%cmake -Wno-dev \
	-DMESHLAB_USE_DEFAULT_BUILD_AND_INSTALL_DIRS:BOOL=ON \
	-DCMAKE_SKIP_RPATH:PATH=ON \
	-DCMAKE_VERBOSE_MAKEFILE:BOOL=OFF \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DALLOW_BUNDLED_EIGEN:BOOL=OFF \
	-DALLOW_BUNDLED_GLEW:BOOL=OFF \
	-DALLOW_BUNDLED_LEVMAR:BOOL=ON \
	-DALLOW_BUNDLED_LIB3DS:BOOL=OFF \
	-DALLOW_BUNDLED_MUPARSER:BOOL=OFF \
	-DALLOW_BUNDLED_NEWUOA:BOOL=ON \
	-DALLOW_BUNDLED_OPENCTM:BOOL=ON \
	-DALLOW_BUNDLED_QHULL:BOOL=OFF \
	-DALLOW_BUNDLED_SSYNTH:BOLL=ON \
	-DALLOW_BUNDLED_XERCES:BOOL=OFF \
	-DALLOW_SYSTEM_EIGEN:BOOL=ON \
	-DALLOW_SYSTEM_GLEW:BOOL=ON \
	-DALLOW_SYSTEM_GMP:BOOL=ON \
	-DALLOW_SYSTEM_LIB3DS:BOOL=ON \
	-DALLOW_SYSTEM_MUPARSER:BOOL=ON \
	-DALLOW_SYSTEM_OPENCTM:BOOL=ON \
	-DALLOW_SYSTEM_QHULL:BOOL=ON \
	-DALLOW_SYSTEM_XERCES:BOOL=ON \
	-DEigen3_DIR=%{_includedir}/eigen3 \
	-DQhull_DIR=%{_includedir}/libqhull \
	-G Ninja
%ninja_build

%install
%ninja_install -C src/build

# icons
for d in 16 32 48 64 72 128 256
do
	install -dm 0755 %{buildroot}%{_iconsdir}/hicolor/${d}x${d}/apps/
	convert -background none -size "${d}x${d}" %{name}.png \
			%{buildroot}%{_iconsdir}/hicolor/${d}x${d}/apps/%{name}.png
done
install -dm 0755 %{buildroot}%{_datadir}/pixmaps/
convert -background none -size "64x64"  %{name}.png \
			%{buildroot}%{_datadir}/pixmaps/%{name}.xpm

# launcher
mv %{buildroot}%{_bindir}/%{name} %{buildroot}%{_bindir}/%{name}-bin
cat > %{buildroot}%{_bindir}/%{name} <<EOF
#!/bin/sh
QT_QPA_PLATFORM=xcb LD_LIBRARY_PATH=/usr/lib64/meshlab:\$LD_LIBRARY_PATH %{name}-bin
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

