CC = gcc

LDFLAGS = -lm #-lSaturn
CFLAGS = -g  #-ftree-vectorize #-Wall  #-finstrument-functions

# comment these in to build with FFMPEG included
LDFLAGS = -L/usr/local/lib -lm -lavbin -lavdevice -lavcodec -lavformat -lavutil -lswscale -lz -lbz2 -lpthread#-lSaturn
CFLAGS = -I/usr/local/include -g -DHAVE_FFMPEG #-ftree-vectorize #-Wall  #-finstrument-functions

pmodules = utilities.o image_lib.o draw_lib.o image_filters.o level_set.o contour_lib.o\
					 water_shed.o
cmodules = common.o tiff_io.o tiff_image.o aip.o eval.o seq.o trace.o\
					 match.o bar.o image_adapt.o error.o adjust_scan_bias.o\
					 seed.o whisker_io.o whisker_io_whisker1.o whisker_io_whiskbin1.o\
					 whisker_io_whiskold.o viterbi.o traj.o compat.o merge.o\
					 svd.o poly.o mat.o\
					 bar_io.o \
					 measurements_io.o measurements_io_v0.o measurements_io_v1.o \
					 whisker_io_whiskpoly1.o \
					 ffmpeg_adapt.o \
           parameters/param.o
modules = $(pmodules) $(cmodules)
TESTS = test_whisker_io evaltest aiptest viterbi_test
APPS  = whisk whisker_convert test_measure_1 test_classify_1 test_hmm_reclassify_3 test_hmm_reclassify_5

LIBS  = libwhisk.so libtraj.so

all: checkos $(APPS) $(LIBS) python #$(TESTS)

rebuild: clean all

.PHONY: checkos
checkos:
ifndef OS
CP = cp
OS =
else
CP = copy
RM = del 
endif

all: $(APPS)

tests: $(TESTS)

whisk: whisk.c $(modules) $(modules:.o=.h)
	$(CC) $(CFLAGS) $+ $(LDFLAGS) -o $@

whisker_io_main.o: whisker_io.c
	$(CC) -c $(CFLAGS) -DWHISKER_IO_CONVERTER $< $(LDFLAGS) -o $@

whisker_convert: whisker_io_main.o $(filter-out whisker_io.o,$(modules)) $(modules:.o=.h)
	$(CC) $(CFLAGS) $+ $(LDFLAGS) -o $@

libwhisk.so: $(modules)
	ar cru $@ $+
	ranlib $@

libtraj.so: traj.o common.o error.o utilities.o viterbi.o report.o
	ar cru $@ $+
	ranlib $@

python: $(LIBS) trace.py traj.py
	$(CP) $+ ./ui/whiskerdata
	$(CP) $+ ./ui

awk: $(pmodules:.o=.toawk)

%.toawk: %.p
	awk -f manager.awk $< > $*.c

%.o: %.p
	awk -f manager.awk $< > $*.c
	$(CC) $(CFLAGS) -c $*.c

$(cmodules): $(cmodules:.o=.h)

test_measure_1: measure.c $(modules)
	$(CC) $(CFLAGS) -DTEST_MEASURE_1 $+ $(LDFLAGS) -o $@

test_classify_1: classify.c utilities.o traj.o common.o error.o viterbi.o measurements_io.o measurements_io_v0.o measurements_io_v1.o parameters/param.o
	$(CC) $(CFLAGS) -DTEST_CLASSIFY_1 $+ $(LDFLAGS) -o $@

test_hmm_reclassify_3: hmm-reclassify.c utilities.o  traj.o  common.o \
                       error.o viterbi.o \
                       hmm-reclassify-lrmodel.o \
                       hmm-reclassify-lrmodel-w-deletions.o \
                       measurements_io.o measurements_io_v0.o measurements_io_v1.o \
                       parameters/param.o
	$(CC) $(CFLAGS) -DTEST_HMM_RECLASSIFY_3 $+ $(LDFLAGS) -o $@

test_hmm_reclassify_5: hmm-reclassify.c utilities.o  traj.o  common.o \
                       error.o viterbi.o \
                       hmm-reclassify-lrmodel.o \
                       hmm-reclassify-lrmodel-w-deletions.o \
                       measurements_io.o measurements_io_v0.o measurements_io_v1.o \
                       parameters/param.o
	$(CC) $(CFLAGS) -DTEST_HMM_RECLASSIFY_5 $+ $(LDFLAGS) -o $@

test_whisker_io: test_whisker_io.c $(modules) 

seedtest: seedtest.c $(modules)

stripetest: stripetest.c $(modules)

evaltest: evaltest.c $(modules)
# 	$(CC) $(LDFLAGS) $(CFLAGS) -DEVAL_TEST_1 $+ -o $@
# 	-./$@
# 	$(CC) $(LDFLAGS) $(CFLAGS) -DEVAL_TEST_2 $+ -o $@
# 	-./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DEVAL_TEST_3 $+ -o $@
	-./$@
##$(CC) $(LDFLAGS) $(CFLAGS) -DEVAL_TEST_4 $+ -o $@
##-./$@
##$(CC) $(LDFLAGS) $(CFLAGS) -DEVAL_TEST_5 $+ -o $@
##-./$@

aiptest: aip.c 
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_1 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_2 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_3 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_4 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_5 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_6 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_7 $< -o $@
	./$@
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_AIP -DTEST_AIP_8 $< -o $@
	./$@

viterbi_test: viterbi.c $(filter-out viterbi.o, $(modules))
	$(CC) $(LDFLAGS) $(CFLAGS) -DTEST_VITERBI $+ -o $@
	./$@

.PHONY: clean
clean: checkos
	-$(RM) *.o $(pmodules:.o=.c)
	-$(RM) *.so
	-$(RM) ./ui/whiskerdata/*.so
	-$(RM) ./ui/*.so
	-$(RM) ./ui/whiskerdata/trace.py
	-$(RM) ./ui/whiskerdata/traj.py
	-$(RM) ./ui/trace.py
	-$(RM) ./ui/traj.py
	-$(RM) *.dll
	-$(RM) *.exe
	-$(RM) *.pyc
	-$(RM) -r *.dSYM
	-$(RM) $(LIBS)
	-$(RM) $(TESTS)
	-$(RM) $(APPS)

.PHONY: superclean
superclean: clean
	-$(RM) *.tif
	-$(RM) gmon.out
	-$(RM) SaturnErrors.txt
	-$(RM) *.whiskers
	-$(RM) *.trajectories
	-$(RM) *.bar
	-$(RM) *.detectorbank
