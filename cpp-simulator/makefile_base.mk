#Set this to -DTIMING to enable timing output
timing = -DTIMING

#Set this to -DDEBUG to enable debugging output
debug =

#Set this to -DMERSENNE_TWISTER to use the Mersenne twister 19937 Random number generator
random = -DMERSENNE_TWISTER

#Get the git commit ID
GIT_HASH = $(shell git rev-parse HEAD)
GIT_TREE_STATE=$(shell (git status --untracked-files=no --porcelain | grep -q .) && echo dirty || echo clean)

include_paths = -Ilibs/ -Ilibs/cxxopts-2.2.0/include/
obj = initializers.o models.o interventions.o intervention_primitives.o updates.o simulator.o testing.o outputs.o drive_simulator.o

DEPFLAGS = -MMD -MP -MF $*.d

CXX = g++
CPPFLAGS = -Wall --std=c++14 -O3 $(DEPFLAGS) $(include_paths) $(parallel) $(timing) $(debug) $(random) -D GIT_HASH='"$(GIT_HASH)"' -D GIT_TREE_STATE='"$(GIT_TREE_STATE)"'

all: drive_simulator check

drive_simulator: $(obj)
	$(CXX) $(CPPFLAGS) $^ -o $@

%.o : $.cc %.d
	$(CXX) $(CPPFLAGS) -c $<

$(DEPDIR):
	mkdir -p $@


DEPFILES := $(obj:%.o=%.d)
$(DEPFILES):


.PHONY: clean
clean:
	rm drive_simulator *.o

.PHONY: check
check:
ifeq ($(GIT_TREE_STATE),dirty)
	$(error git state is not clean)
endif

include $(wildcard $(DEPFILES))
