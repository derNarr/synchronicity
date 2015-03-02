################
## ducks_boat_20
################

FOLDER <- "sim_data_velocity_ducks_boat_20_number16"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_nanmean

dat.velocity <- dat
rm(dat)


FOLDER <- "sim_data_velocity_ducks_boat_20_number6"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_nanmean

dat.velocity2 <- dat
rm(dat)


FOLDER <- "sim_data_velocity_ducks_boat_20_number16"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_nanmean

dat.velocity3 <- dat
rm(dat)



FOLDER <- "sim_data_location_ducks_boat_20"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_nanmean

dat.location <- dat
rm(dat)

rm(files, FOLDER, file)


png(paste("velocity_location_ducks_boat_20", ".png", sep=""), 3900, 1200, res=300)

plot(coherence ~ I(t/1000000), dat.velocity2,
     type="l", xlim=c(0.5, 19.5), ylim=c(-1.0, 2.0), xlab="Zeit in Sekunden",
     ylab="Synchronizität", col="blue", lty=2,
     main="Synchronizität im Ducks Boat Video")
points(coherence ~ I(t/1000000), dat.velocity, type="l", col="black", lwd=2)
#points(coherence ~ I(t/1000000), dat.velocity3, type="l", col="green")
#points(coherence ~ I(t/1000000), dat.location, type="l", col="red")
abline(v=2.0, lty=3, lwd=2)
abline(v=11.0, lty=3, lwd=2)
legend("topright", c("naive", "polar"), lwd=c(1, 2), col=c("blue", "black"), lty=c(2,1))

dev.off()


###################
## Random Intervals
###################

FOLDER <- "sim_data_velocity_random_intervals_100"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_mean

dat.velocity <- dat


FOLDER <- "sim_data_random_intervals_100_number2"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat.location <- dat[dat$method == "xy-population",]

rm(dat, files, FOLDER, file)


png(paste("velocity_location_random_locations", ".png", sep=""), 800, 400)
plot(coherence ~ t, dat.velocity,
     type="l", ylim=c(-1.0, 1.0), xlab="time in us", ylab="Coherence C(t)")
points(coherence ~ t, dat.location, type="l", col="red")
dev.off()

png(paste("velocity_location_random_locations_zoom", ".png", sep=""), 800, 400)
dat.velocity.2 <- dat.velocity[dat.velocity$t > 4000000 & dat.velocity$t < 8000000,]
dat.location.2 <- dat.location[dat.location$t > 4000000 & dat.location$t < 8000000,]
plot(coherence ~ t, dat.velocity.2, type="l", ylim=c(-1.0, 1.0))
points(coherence ~ t, dat.location.2, type="l", col="red")
dev.off()


####################
## Breite Strasse 20
####################

FOLDER <- "sim_data_velocity_breite_strasse_20_number8"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_mean

dat.strasse.vel <- dat


FOLDER <- "sim_data_breite_strasse_20_number2"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_mean

dat.strasse.loc <- dat[dat$method == "xy-population",]

rm(dat, files, FOLDER, file)

png(paste("velocity_location_breite_strasse_20", ".png", sep=""), 800, 400)
plot(coherence ~ t, dat.strasse.vel,
     type="l", ylim=c(-1.0, 12), xlab="time in us", ylab="Coherence C(t)")
points(coherence ~ t, dat.strasse.loc, type="l", col="red")
dev.off()


# std_t
#######

folders <- dir(pattern="sim_data_velocity_breite_strasse_20_number*")

dat <- data.frame()
for (folder in folders) {
    files <- dir(folder)

    for (file in files) {
        tmp <- read.table(paste(folder, file, sep="/"), header=T)
        dat <- rbind(dat, tmp)
    }
    rm(tmp)
}

dat <- dat[order(dat$method, dat$SIGMA_X, dat$t),]

dat$coherence <- dat$nss_mean

dat.strasse.vel <- dat


FOLDER <- "sim_data_breite_strasse_20_number2"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_mean

dat.strasse.loc <- dat[dat$method == "xy-population",]

rm(dat, files, FOLDER, file)

library(lattice)

xyplot(coherence ~ t, groups=SIGMA_X, data=dat.strasse.vel, xlim=c(0, 2000000), type="l")


plot(coherence ~ t, dat.strasse.vel[dat.strasse.vel$SIGMA_X == 50,],
     xlim=c(0, 2000000), ylim=c(-1, 12), type="l", lwd=2)
abline(v=60000, lty=2, lwd=3)
abline(v=240000, lty=2, lwd=3)
abline(v=720000, lty=2, lwd=3)
points(coherence ~ t, dat.strasse.loc, col="green", type="l", lwd=2)

sigma_xs = c(1e-1, 4e-2, 1e-2, 5e-3, 2e-3, 1e-3, 5e-4, 1e-4, 1e-5, 1e-6)
colors = c("#111111", "#222222", "#333333", "#444444", "#555555",
             "#666666", "#777777", "#888888", "#999999", "#AAAAAA")
for (ii in 1:length(sigma_xs)) {
    print(sigma_xs[ii])
    points(coherence ~ t, dat.strasse.vel[dat.strasse.vel$SIGMA_X ==
           sigma_xs[ii],], col=colors[ii], type="l", lwd=2)
}


plot(coherence ~ log(SIGMA_X), dat.strasse.vel[dat.strasse.vel$t ==
     60000,], type="b")
points(coherence ~ log(SIGMA_X), dat.strasse.vel[dat.strasse.vel$t ==
       240000,], type="b", col="red")
points(coherence ~ log(SIGMA_X), dat.strasse.vel[dat.strasse.vel$t ==
       720000,], type="b", col="blue")
abline(v=log(0.0125), lty=2)
abline(v=log(0.0025), lty=3)
legend("topright", c("t=60ms", "t=240ms", "t=720ms", "v=50pix/4ms",
                     "v=10pix/4ms"), lty=c(1, 1, 1, 2, 3), col=c("black",
                     "red", "blue", "black", "black"))

plot(coherence ~ t, dat.strasse.vel[dat.strasse.vel$SIGMA_X == 1e-2,],
     xlim=c(0, 2000000), ylim=c(3.2, 7), type="l", lwd=2)

sigma_xs = c(1e-2, 5e-3, 2e-3, 1e-3)
colors = c("#222222", "#444444", "#666666", "#888888")
sigma_xs = c(1e-2, 1e-3)
colors = c("#222222", "#888888")
for (ii in 1:length(sigma_xs)) {
    print(sigma_xs[ii])
    points(coherence ~ t, dat.strasse.vel[dat.strasse.vel$SIGMA_X ==
           sigma_xs[ii],], col=colors[ii], type="l", lwd=2)
}
points(I(coherence + 3.2) ~ t, dat.strasse.loc, col="green", type="l", lwd=2)


##############
## One-Subject
##############

FOLDER <- "sim_data_velocity_breite_strasse_subject_1"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_mean

dat.strasse.vel <- dat


FOLDER <- "sim_data_breite_strasse_subject_1"
files <- dir(FOLDER)

dat <- read.table(paste(FOLDER, files[1], sep="/"), header=T)
for (file in files[-1]) {
    tmp <- read.table(paste(FOLDER, file, sep="/"), header=T)
    dat <- rbind(dat, tmp)
}
rm(tmp)
dat <- dat[order(dat$method, dat$t),]

dat$coherence <- dat$nss_mean

dat.strasse.loc <- dat[dat$method == "xy-population",]

rm(dat, files, FOLDER, file)

png(paste("velocity_location_breite_strasse_subject1", ".png", sep=""), 800, 400)
plot(coherence ~ t, dat.strasse.vel,
     type="l", ylim=c(-1.0, 22), xlab="time in us", ylab="Coherence C(t)")
points(coherence ~ t, dat.strasse.loc, type="l", col="red")
dev.off()


############
## Sonstiges
############

tmp <- dat[dat$method=="xy-population", c(2, 7)]
tmp <- tmp[!duplicated(tmp$t),]
tmp$coherence[is.na(tmp$coherence)] <- mean(tmp$coherence, na.rm=T)
dat.pop <- tmp$coherence
tmp <- dat[dat$method=="xy-grid", c(2, 7)]
tmp <- tmp[!duplicated(tmp$t),]
tmp$coherence[is.na(tmp$coherence)] <- mean(tmp$coherence, na.rm=T)
dat.xyg <- tmp$coherence
tmp <- dat[dat$method=="xyt-grid", c(2, 7)]
tmp <- tmp[!duplicated(tmp$t),]
tmp$coherence[is.na(tmp$coherence)] <- mean(tmp$coherence, na.rm=T)
dat.xytg <- tmp$coherence

layout(matrix(c(1,2,3), nrow=3))
acf(dat.pop)
acf(dat.xyg)
acf(dat.xytg)

layout(matrix(c(1,2,3), nrow=3))
pacf(dat.pop)
pacf(dat.xyg)
pacf(dat.xytg)







dat.n_norm <- aggregate(cbind(comp_time, coherence)~n_norm,
                      dat[dat$method=="xy-population",], mean)
names(dat.n_norm) <- c("n_norm", "comp_time", "coh_mean")
dat.n_norm$coh_sd <- aggregate(coherence~n_norm,
                       dat[dat$method=="xy-population",], sd)$coherence
dat.n_norm$coh_min <- aggregate(coherence~n_norm,
                       dat[dat$method=="xy-population",], min)$coherence
dat.n_norm$coh_max <- aggregate(coherence~n_norm,
                       dat[dat$method=="xy-population",], max)$coherence
dat.n_norm$prop_3sd <- with(dat.n_norm, 3*coh_sd/coh_mean)
dat.n_norm$prop_minmax <- with(dat.n_norm, (coh_max - coh_min)/coh_mean)


plot(coherence ~ I(log10(n_norm)-0.1), dat[dat$method=="xy-population",])
points(coherence ~ I(log10(n_norm)-0.1), n_norm.m[n_norm.m$method=="xy-population",],
       type="b", lwd=2)

points(coherence ~ I(n_norm+0.1), dat[dat$method=="xy-grid",], col="blue", pch="x")
points(coherence ~ I(n_norm+0.1), n_norm.m[n_norm.m$method=="xy-grid",], type="b",
       col="blue", lty=2, lwd=2)

points(coherence ~ I(n_norm+0.1), dat[dat$method=="xyt-grid",],
       col="purple", pch=18)
points(coherence ~ I(n_norm+0.1), n_norm.m[n_norm.m$method=="xyt-grid",],
       type="b", col="purple", lty=2, lwd=2)

