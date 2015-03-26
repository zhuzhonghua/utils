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
