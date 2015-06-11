;(setq debug-on-error t)
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(ecb-options-version "2.40")
 '(lua-indent-level 4)
 '(org-agenda-files (quote ("e:/TODO.org")))
 '(show-paren-mode t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(default ((t (:family "Consolas" :foundry "outline" :slant normal :weight normal :height 120 :width normal)))))

(global-visual-line-mode t)
(global-linum-mode 1)
(show-paren-mode)

(require 'color-theme)
(color-theme-initialize)
;;(color-theme-charcoal-black)
;;(color-theme-classic)
;(color-theme-dark-blue)
;(require 'yasnippet)
;(yas-global-mode 1)

(require 'color-theme-solarized)
(color-theme-solarized-dark)

;(load-theme 'wombat t)

(require 'js2-mode)
(add-to-list 'auto-mode-alist '("\\.js\\'" . js2-mode))

;;(require 'node-ac-mode)
;(setq node-ac-node-modules-path "E:/Project/MageTower/Version/trunk/Server/node_modules")
;
;(add-hook 'js2-mode-hook
;          (lambda ()
;            (local-set-key (kbd "C-.") 'node-ac-auto-complete)
;            (local-set-key (kbd "C-c C-d") 'node-ac-show-document)
;            (local-set-key (kbd "C-c C-j") 'node-ac-jump-to-definition)
;            (local-unset-key (kbd "<tab>"))))

; cedet
;(require 'cedet)
;(global-ede-mode t)
;(require 'ecb)
;(setq ecb-layout-name "left15")
; end cedet

;(require 'tabbar)
;(tabbar-mode 1)

(setq-default indent-tabs-mode nil)
(setq-default tab-width 4)
;(setq indent-line-function 'insert-tab)

(setq frame-title-format 
'("%S" (buffer-file-name "%f" 
        (dired-directory dired-directory "%b"))))

;(global-set-key (kbd "M-h") 'tabbar-backward)
;(global-set-key (kbd "M-l") 'tabbar-forward)

(require 'auto-complete-config)
(ac-config-default)

(setq make-backup-files nil)

(require 'ace-window)

(global-set-key (kbd "C-=") 'ace-window)

(global-set-key (kbd "C-o") '(lambda ()
                               (interactive)
                               (if (< (line-number-at-pos) 2)
                                   (progn
                                     (beginning-of-visual-line)
                                     (newline-and-indent)
                                     (previous-line))
                                 (progn
                                   (previous-line)
                                   (end-of-visual-line)
                                   (newline-and-indent)))))
                

(global-set-key (kbd "C-<return>") '(lambda ()
                                    (interactive)
                                    (end-of-visual-line)
                                    (newline-and-indent)))

(global-set-key (kbd "C-z") 'undo)
(global-set-key (kbd "C-,") '(lambda (&optional arg)
                               (interactive "P")
                               (print arg)
                               (if arg
                                 (progn (delete-other-windows)
                                        (mapc 'kill-buffer
                                              (cdr (buffer-list (current-buffer)))))
                                   (kill-buffer))))

(global-set-key (kbd "C-;") '(lambda ()
                               (interactive)
                               (save-buffer (current-buffer))))
(setq inhibit-startup-message t)


(require 'yasnippet)
(yas-global-mode 1)

(require 'ido)
(ido-mode t)

;;
;;(eval-when-compile (require 'cl)) 
;;
;;(defun set-font (english chinese english-size chinese-size) 
;;  (set-face-attribute 'default nil :font 
;;                      (format "%s:pixelsize=%d" english english-size)) 
;;  (dolist (charset '(kana han symbol cjk-misc bopomofo)) 
;;    (set-fontset-font (frame-parameter nil 'font) charset 
;;                      (font-spec :family chinese :size chinese-size)))) 
;;
;;(ecase system-type 
;;  (gnu/linux 
;;   (set-face-bold-p 'bold nil) 
;;   (set-face-underline-p 'bold nil) 
;;   (set-font "monofur" "vera Sans YuanTi Mono" 20 20)) 
;;  (darwin 
;;   (set-font "monofur" "STHeiti" 20 20))
;;  (windows-nt
;;   (set-face-bold-p 'bold nil) 
;;   (set-face-underline-p 'bold nil) 
;;   (set-font "monaco" "vera Sans YuanTi Mono" 16 26)))
;;
;;(set-frame-font "Ubuntu Mono 12")
;;(ecase system-type 
;;  (gnu/linux
;;   (set-fontset-font t 'han (font-spec :family "WenQuanYi Micro Hei Mono")))
;;  (windows-nt
;;   (set-fontset-font t 'han (font-spec :family "Microsoft Yahei"))))

;;(set-frame-font "Monaco:pixelsize=14");
;;(dolist (charset '(han kana symbol cjk-misc bopomofo))  (set-fontset-font (frame-parameter nil 'font) charset
;;      (font-spec :family "WenQuanYi Micro Hei Mono" :size 16)))

;;(defvar emacs-english-font "Monaco"
;;  "The font name of English.")
;;
;;(defvar emacs-cjk-font "Hiragino Sans GB W3"
;;  "The font name for CJK.")
;;
;;(defvar emacs-font-size-pair '(15 . 18)
;;  "Default font size pair for (english . chinese)")
;;
;;(defvar emacs-font-size-pair-list
;;  '(( 5 .  6) (10 . 12)
;;    (13 . 16) (15 . 18) (17 . 20)
;;    (19 . 22) (20 . 24) (21 . 26)
;;    (24 . 28) (26 . 32) (28 . 34)
;;    (30 . 36) (34 . 40) (36 . 44))
;;  "This list is used to store matching (englis . chinese) font-size.")
;;
;;(defun font-exist-p (fontname)
;;  "Test if this font is exist or not."
;;  (if (or (not fontname) (string= fontname ""))
;;      nil
;;    (if (not (x-list-fonts fontname)) nil t)))
;;
;;(defun set-font (english chinese size-pair)
;;  "Setup emacs English and Chinese font on x window-system."
;;
;;  (if (font-exist-p english)
;;      (set-frame-font (format "%s:pixelsize=%d" english (car size-pair)) t))
;;
;;  (if (font-exist-p chinese)
;;      (dolist (charset '(kana han symbol cjk-misc bopomofo))
;;        (set-fontset-font (frame-parameter nil 'font) charset
;;                          (font-spec :family chinese :size (cdr size-pair))))))
;;
;;(set-font emacs-english-font emacs-cjk-font emacs-font-size-pair)
;;
;;(defun emacs-step-font-size (step)
;;  "Increase/Decrease emacs's font size."
;;  (let ((scale-steps emacs-font-size-pair-list))
;;    (if (< step 0) (setq scale-steps (reverse scale-steps)))
;;    (setq emacs-font-size-pair
;;          (or (cadr (member emacs-font-size-pair scale-steps))
;;              emacs-font-size-pair))
;;    (when emacs-font-size-pair
;;      (message "emacs font size set to %.1f" (car emacs-font-size-pair))
;;      (set-font emacs-english-font emacs-cjk-font emacs-font-size-pair))))
;;
;;(defun increase-emacs-font-size ()
;;  "Decrease emacs's font-size acording emacs-font-size-pair-list."
;;  (interactive) (emacs-step-font-size 1))
;;
;;(defun decrease-emacs-font-size ()
;;  "Increase emacs's font-size acording emacs-font-size-pair-list."
;;  (interactive) (emacs-step-font-size -1))

;; Setting English Font 
(set-face-attribute 
 'default nil :font "Consolas 14") 
;; Chinese Font 
(dolist (charset '(kana han symbol cjk-misc bopomofo)) 
  (set-fontset-font (frame-parameter nil 'font) 
                    charset 
                    (font-spec :family "Microsoft Yahei" :size 20)))

(require 'package)
(add-to-list 'package-archives
             '("melpa" . "http://melpa.org/packages/") t)
(when (< emacs-major-version 24)
  ;; For important compatibility libraries like cl-lib
  (add-to-list 'package-archives '("gnu" . "http://elpa.gnu.org/packages/")))
(package-initialize)

(projectile-global-mode)
(setq projectile-indexing-method 'native)

(global-set-key (kbd "C-<tab>") '(lambda ()
                               (interactive)
                               (switch-to-buffer nil)))
(autoload 'lua-mode "lua-mode" "Lua editing mode." t)
(add-to-list 'auto-mode-alist '("\\.lua$" . lua-mode))
(add-to-list 'interpreter-mode-alist '("lua" . lua-mode))
(add-hook 'lua-mode-hook
		  (lambda ()
			(setq indent-tabs-mode t)))

(setq exec-path (add-to-list 'exec-path "C:/Program Files (x86)/Gow/bin"))
(setenv "PATH" (concat "C:\\Program Files (x86)\\Gow\\bin;" (getenv "PATH")))  
