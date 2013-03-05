(custom-set-variables
  ;; custom-set-variables was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 )
(custom-set-faces
  ;; custom-set-faces was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 120 :width normal :foundry "unknown" :family "DejaVu Sans Mono")))))

(add-to-list 'load-path "~/.emacs.d/slime/")
(setq inferior-lisp-program "/usr/bin/clisp")
(require 'slime)
(slime-setup)

(global-linum-mode t)
(setq-default make-backup-files nil)
(show-paren-mode t)

(setq c-basic-offset 4)
(setq tab-width 4)
      

(defun my-new-line-indent ()
  (interactive)
  (newline-and-indent)
  (previous-line)
  (indent-for-tab-command))

(defun my-hook ()
  (define-key c-mode-base-map "\C-o" 'my-new-line-indent))

(add-hook 'c-mode-common-hook 'my-hook)
