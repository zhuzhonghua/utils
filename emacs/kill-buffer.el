(global-set-key (kbd "C-,") '(lambda (&optional arg)
                               (interactive "P")
                               (print arg)
                               (if arg
                                 (progn (delete-other-windows)
                                        (mapc 'kill-buffer
                                              (cdr (buffer-list (current-buffer)))))
                                   (kill-buffer))))
