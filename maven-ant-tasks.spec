Name:           maven-ant-tasks
Version:        2.1.1
Release:        10
Summary:        Allow Maven artifact handling features to be used from within an Ant build

Group:          Development/Java
License:        ASL 2.0
URL:            http://maven.apache.org/ant-tasks/index.html
#The ant-tasks-in-ant-run-plugin test needs a dependency on ant-launcher
#http://jira.codehaus.org/browse/MANTTASKS-208
Source0:        http://www.apache.org/dist/maven/source/maven-ant-tasks-%{version}-src.zip
Source1:        %{name}.depmap
#Fix up ant groupId
Patch0:         maven-ant-tasks-2.1.1-ant-groupId.patch
BuildArch:      noarch

BuildRequires:  jpackage-utils
BuildRequires:  java-devel
BuildRequires:  ant >= 1.8.0
BuildRequires:  maven2
BuildRequires:  maven-antrun-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-invoker-plugin
BuildRequires:  maven-jar-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-shade-plugin
BuildRequires:  maven-surefire-maven-plugin
BuildRequires:  objectweb-asm
BuildRequires:  plexus-interpolation

Requires:       jpackage-utils

Requires(post):       jpackage-utils
Requires(postun):     jpackage-utils

Requires:       java

%description
Maven Ant Tasks allow several of Maven's artifact handling features to be
used from within an Ant build. These include:

* Dependency management - including transitive dependencies, scope recognition
  and SNAPSHOT handling
* Artifact deployment - deployment to a Maven repository (file integrated,
  other with extensions)
* POM processing - for reading and writing a Maven 2 pom.xml file


%package javadoc
Summary:        Javadocs for %{name}
Group:          Development/Java
Requires:       jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.


%prep
%setup -q
%patch0 -p1 -b .ant-groupId
#Need to tell maven invoker to run in jpp mode, write test.properties files
for f in src/it/*/invoker.properties
do
   tp=${f/invoker/test}
   cat >> $tp <<EOF
maven2.jpp.mode=1
EOF
done


%build
#We need to use their local repo becase we can't override it
export MAVEN_REPO_LOCAL=$(pwd)/target/local-repo
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven2.jpp.depmap.file="%{SOURCE1}" \
        install javadoc:javadoc


%install

mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p target/original-%{name}-%{version}.jar \
      $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

mkdir -p $RPM_BUILD_ROOT%{_javadocdir}
cp -rp target/site/apidocs \
       $RPM_BUILD_ROOT%{_javadocdir}/%{name}

install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 pom.xml \
        $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom

%add_to_maven_depmap org.apache.maven %{name} %{version} JPP %{name}


%pre javadoc
# workaround for rpm bug, can be removed in F-17
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%post
%update_maven_depmap

%postun
%update_maven_depmap


%files
%defattr(-,root,root,-)
%doc DEPENDENCIES LICENSE NOTICE README.txt
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*
%{_javadir}/*

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE
%{_javadocdir}/%{name}


