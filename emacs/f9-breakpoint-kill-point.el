(global-set-key [(f9)] '(lambda ()
                               (interactive)
                               (save-excursion
                                 (if (eq (car (fringe-bitmaps-at-pos (point))) 'breakpoint)
                                     (gud-remove nil)
                                   (gud-break nil)))))

(add-hook 'gdb-mode-hook (lambda () (fringe-mode)))