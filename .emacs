(set 'tab-width 4)
(set 'default-tab-width 4)
(set 'c-basic-offset 4)
(set 'tab-always-indent nil)
(set 'c-tab-always-indent nil)

(setq make-backup-files nil)

(global-linum-mode t)
(delete-selection-mode 1)
(show-paren-mode)

;;tab
;;(defun my-tab ()
;;  (interactive)
;;  (let* ((ci (current-indentation))
;;		 (mo (% ci c-basic-offset)))
;;	(if (not (= 0 mo))
;;	(indent-for-tab-command))))

;;c-o
(defun my-c-o ()
  ""
  (interactive)
  (if (not (= 1 (line-number-at-pos)))
	  (progn
		(previous-line)
		(move-end-of-line 1)
		(newline-and-indent))
	(save-excursion
	  (newline-and-indent))))

(global-set-key "\C-o" 'my-c-o)

(defun my-c++-tab ()
  (interactive)
  (setq old-pos (point))
  (indent-for-tab-command)
  (setq new-pos (point))
  (if (= old-pos new-pos)
	  (c-shift-line-indentation tab-width)))

(add-hook 'c++-mode-hook '(lambda ()
						   (define-key c++-mode-map (kbd "TAB") 'my-c++-tab)))

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
 '(default ((t (:inherit nil :stipple nil :background "white" :foreground "black" :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 120 :width normal :foundry "bitstream" :family "Courier 10 Pitch")))))
