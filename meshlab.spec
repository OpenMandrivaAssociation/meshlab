%define oname MeshLab
%define name %(echo %oname | tr [:upper:] [:lower:])

Summary:	An open source system for processing and editing 3D triangular meshes
Name:		meshlab
Version:	2022.02
Release:	2
Group:		Graphics
License:	GPLv2+ and BSD and Public Domain and ASL 2.0
URL:		https://github.com/cnr-isti-vclab/%{name}
Source0:	https://github.com/cnr-isti-vclab/%{name}/archive/%{oname}-%{version}/%{name}-%{version}.tar.gz
# FIXME: actually can't be build as a indipendent library
Source10:	https://github.com/cnr-isti-vclab/vcglib/archive/%{version}/vcglib-%{version}.tar.gz

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	boost-devel
#BuildRequires:	cgal-devel
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(eigen3)
BuildRequires:	pkgconfig(glew)
BuildRequires: 	pkgconfig(glu)
BuildRequires: 	pkgconfig(gmp)
BuildRequires:	pkgconfig(lib3ds)
BuildRequires:	pkgconfig(libexif)
BuildRequires:	pkgconfig(muparser)
BuildRequires:	pkgconfig(xerces-c)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	qhull-devel
BuildRequires:	qt5-qtbase-devel
# (unpackaged)
#BuildRequires:	levmar-devel

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
%autosetup -n %{name}-%{oname}-%{version} -a 10

# use vcglib from source
rm -fr src/vcglib
mv vcglib-%{version} src/vcglib

# remove some bundles
for lib in glew qhull lib3ds muparser #levmar
do
	rm -rf src/external/${lib}{-,_}*
done

# fix plugin path
sed -i -e 's|"lib"|"%{_lib}"|g' src/common/globals.cpp

%build
%global cpp_std c++17

export CMAKE_BUILD_DIR=src/build
%cmake \
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

