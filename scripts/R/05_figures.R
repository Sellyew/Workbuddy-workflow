# =============================================================================
# 05_figures.R — Figures → PDF and SVG.
#
# PDF for Beamer (crisp vector). SVG for Quarto slides (native browser render).
# Both from the same ggplot object so there's one source of truth per figure.
# =============================================================================

if (!exists("df", inherits = FALSE)) {
  stop("05_figures.R: df missing. Run 00_run_all.R (not this script directly).")
}
if (!exists("OUT_DIR", inherits = FALSE)) {
  stop("05_figures.R: OUT_DIR missing. Run 00_run_all.R (not this script directly).")
}
# Re-seed for reproducibility if geom_jitter or anything else pulls RNG.
if (exists("PROJECT_SEED", inherits = FALSE)) {
  set.seed(PROJECT_SEED)
}

# ggplot2 is a HARD dependency — figure quality is not negotiable and silent
# fallback to base-R plotting breaks the reproducibility contract (two forks
# would emit different outputs with no failure signal). See scripts/R/README.md.
if (!requireNamespace("ggplot2", quietly = TRUE)) {
  stop(
    "05_figures.R: 'ggplot2' is required for figure generation and is not installed.\n",
    "Install with: install.packages('ggplot2')\n",
    "The pipeline will not silently fall back to base-R plots."
  )
}

# svglite is OPTIONAL but documented. If absent, fail LOUDLY (warning + explicit
# note in the output list) rather than silently skipping a promised artifact.
has_svg <- requireNamespace("svglite", quietly = TRUE)

# cairo_pdf gives nicer anti-aliasing and font embedding, but capabilities("cairo")
# only says cairo was compiled in: on macOS without XQuartz it reports TRUE and the
# library then fails to load, so the device never opens and ggsave silently draws
# into Rplots.pdf instead (issue #156). Decide by actually opening the device.
cairo_works <- function() {
  if (!isTRUE(tryCatch(capabilities("cairo"), error = function(e) FALSE))) return(FALSE)
  probe  <- tempfile(fileext = ".pdf")
  before <- grDevices::dev.list()
  ok <- tryCatch({
    suppressWarnings(grDevices::cairo_pdf(probe))
    opened <- setdiff(grDevices::dev.list(), before)
    if (length(opened) > 0) grDevices::dev.off(opened[1])
    length(opened) > 0 && file.exists(probe)
  }, error = function(e) FALSE)
  unlink(probe)
  isTRUE(ok)
}

# A promised figure either exists and is non-empty, or the run stops naming it.
save_checked <- function(path, plot, device) {
  unlink(path)
  ggsave(path, plot, width = 5, height = 3.5, device = device)
  if (!file.exists(path) || file.size(path) == 0) {
    stop("05_figures.R: ", path, " was not written (the graphics device failed). ",
         "Nothing was silently skipped; fix the device and re-run 00_run_all.R.")
  }
  message("Wrote ", path)
}

fig_main_pdf <- file.path(OUT_DIR, "fig_main.pdf")
fig_main_svg <- file.path(OUT_DIR, "fig_main.svg")

pdf_device <- if (cairo_works()) grDevices::cairo_pdf else grDevices::pdf

library(ggplot2)

p <- ggplot(df, aes(x = factor(treated, labels = c("Control", "Treated")),
                    y = delta)) +
  geom_boxplot(width = 0.5, fill = "#E8EDF5", color = "#012169") +
  geom_jitter(width = 0.1, alpha = 0.4, color = "#1A1A1A") +
  labs(x = NULL, y = expression(Delta == y[post] - y[pre])) +
  theme_minimal(base_size = 12) +
  theme(
    panel.grid.minor = element_blank(),
    axis.text = element_text(color = "#1A1A1A")
  )

save_checked(fig_main_pdf, p, pdf_device)

if (has_svg) {
  save_checked(fig_main_svg, p, svglite::svglite)
} else {
  # Loud skip — warning() not message() so it shows up in `summary(sessionInfo())`
  # and in any CI log that collects warnings.
  warning(
    "05_figures.R: 'svglite' not installed — skipping fig_main.svg.\n",
    "Quarto slides that expect the SVG will fail to render this figure.\n",
    "Install with: install.packages('svglite')",
    call. = FALSE
  )
  message("SKIPPED: ", fig_main_svg, " (svglite missing)")
}
