;;; yamlog.el --- Simple visualization of yam logs   -*- lexical-binding: t; -*-

;; Copyright (C) 2017  Caltech
;; Author: Dima Kogan <Dmitriy.Kogan@jpl.nasa.gov>
;;; Code:


(defvar yamlog-error-face   'error   "Face name for error")
(defvar yamlog-warning-face 'warning "Face name for warning")

;; purposely not highlighting level0. These are just notes
(setq yamlog-highlight-levels
      '( ("^level[2-9].*" . yamlog-error-face)
         ("^level1.*"     . yamlog-warning-face) ))



(define-derived-mode yamlog-mode fundamental-mode "YAM log"
  "Major mode for coloring the logging levels in YAM logs"

  (setq font-lock-defaults '(yamlog-highlight-levels t)))


(add-to-list 'auto-mode-alist '("/yamlog\\.[^/]+[0-9]$" . yamlog-mode))

(provide 'yamlog)
