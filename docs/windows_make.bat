cd source
del *context_menu*
cd ..
sphinx-apidoc -o source/ ../../context_menu ../../context_menu/*setup* ../../context_menu/*tests*
del build /Q
make.bat html