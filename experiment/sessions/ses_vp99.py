# show and run can be used
run_trial(rws[6], duration=8.0)
run_trial(rbs[24], duration=8.0)
show(u'Machen Sie eine kurze Pause.\n\nWeiter mit Leertaste.', wait_keys=('space',))

run_trial(msm2, duration=5.000, speed=300)
run_trial(mem2, duration=4.000, speed=400)
run_trial(hori1, duration=8.000, speed=150)

run_movie(movie1audio, 'Jetzt folgt ein Video mit Ton.\n\nWeiter mit Leertaste')
