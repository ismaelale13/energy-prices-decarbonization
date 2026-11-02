# Rambachan & Roth (2023) sensitivity analysis with the official HonestDiD package.
# Reads event-study estimates exported by src/export_event_study.py.
# Run from the repository root:  Rscript src/honestdid.R
# Output: output/tables/honestdid_rm.csv, output/tables/honestdid_sd.csv

if (!requireNamespace("HonestDiD", quietly = TRUE)) install.packages("HonestDiD", repos = "https://cloud.r-project.org")
suppressPackageStartupMessages(library(HonestDiD))

in_dir <- "output/honestdid"
names  <- c("h1_ln_ci", "h2_ln_emissions", "h2_ln_real_ci", "h2_ln_real_revenue")
rm_out <- list(); sd_out <- list()

for (nm in names) {
  beta  <- read.csv(file.path(in_dir, paste0(nm, "_beta.csv")))$beta
  sigma <- as.matrix(read.csv(file.path(in_dir, paste0(nm, "_sigma.csv")), check.names = FALSE))
  meta  <- read.csv(file.path(in_dir, paste0(nm, "_meta.csv")))
  npre  <- meta$numPrePeriods; npost <- meta$numPostPeriods
  l_vec <- as.numeric(strsplit(meta$l_vec, ";")[[1]])

  orig <- constructOriginalCS(betahat = beta, sigma = sigma, numPrePeriods = npre,
                              numPostPeriods = npost, l_vec = l_vec)

  # Relative magnitudes: post-period violations at most Mbar times the largest pre-period violation
  rm <- createSensitivityResults_relativeMagnitudes(betahat = beta, sigma = sigma, numPrePeriods = npre,
                                                    numPostPeriods = npost, l_vec = l_vec,
                                                    Mbarvec = c(0, 0.25, 0.5, 0.75, 1, 1.5, 2))
  rm_out[[nm]] <- rbind(data.frame(outcome = nm, Mbar = NA, lb = orig$lb, ub = orig$ub, method = "Original"),
                        data.frame(outcome = nm, Mbar = rm$Mbar, lb = rm$lb, ub = rm$ub, method = rm$method))

  # Smoothness: deviations from a linear pre-trend bounded by M per period
  sd <- createSensitivityResults(betahat = beta, sigma = sigma, numPrePeriods = npre,
                                 numPostPeriods = npost, l_vec = l_vec,
                                 Mvec = c(0, 0.01, 0.02, 0.05, 0.1))
  sd_out[[nm]] <- data.frame(outcome = nm, M = sd$M, lb = sd$lb, ub = sd$ub, method = sd$method)
  cat(nm, "done\n")
}

write.csv(do.call(rbind, rm_out), "output/tables/honestdid_rm.csv", row.names = FALSE)
write.csv(do.call(rbind, sd_out), "output/tables/honestdid_sd.csv", row.names = FALSE)
cat("Saved output/tables/honestdid_rm.csv and honestdid_sd.csv\n")
