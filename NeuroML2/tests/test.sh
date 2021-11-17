set -e

jnml Scoping.xml -nogui
echo "---  Output from jNeuroML"
cat test.dat
rm test.dat

pynml Scoping.xml -nogui
echo "---  Output from pyNeuroML"
cat test.dat
