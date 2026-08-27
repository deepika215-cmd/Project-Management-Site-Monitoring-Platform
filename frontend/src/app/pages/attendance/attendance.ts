import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { Api } from '../../services/api';
import { AppSidebarComponent } from '../../shared/app-sidebar.component';

@Component({
    selector: 'app-attendance',
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        AppSidebarComponent
    ],
    templateUrl: './attendance.html',
    styleUrl: './attendance.css'
})
export class Attendance implements OnInit {

    records: any[] = [];
    workers: any[] = [];

    loading = false;
    saving = false;
    error = '';

    form = {
        worker_id: 0,
        date: new Date().toISOString().slice(0, 10),
        status: 'Present'
    };

    constructor(private api: Api) { }

    ngOnInit(): void {
        this.load();
    }

    load(): void {
        this.loading = true;
        this.error = '';

        this.api.getWorkers().subscribe({
            next: (workers) => {
                this.workers = workers || [];

                this.api.getAttendance().subscribe({
                    next: (records) => {
                        this.records = records || [];
                        this.loading = false;
                    },

                    error: (err) => {
                        console.error('Attendance API error:', err);

                        this.records = [];
                        this.loading = false;

                        this.error =
                            err?.error?.detail ||
                            err?.message ||
                            'Unable to load attendance records.';
                    }
                });
            },

            error: (err) => {
                console.error('Workers API error:', err);

                this.workers = [];
                this.records = [];
                this.loading = false;

                this.error =
                    err?.error?.detail ||
                    err?.message ||
                    'Unable to connect to the workers API.';
            }
        });
    }

    save(): void {
        this.error = '';

        if (!this.form.worker_id) {
            this.error = 'Please select a worker.';
            return;
        }

        if (!this.form.date) {
            this.error = 'Please select a date.';
            return;
        }

        if (!this.form.status) {
            this.error = 'Please select an attendance status.';
            return;
        }

        this.saving = true;

        this.api.createAttendance({
            worker_id: this.form.worker_id,
            date: this.form.date,
            status: this.form.status
        }).subscribe({
            next: () => {
                this.saving = false;

                // Reset the worker selection after successful submission
                this.form.worker_id = 0;

                // Reload the attendance records
                this.load();
            },
            error: (err) => {
                console.error('Attendance save error:', err);

                this.saving = false;
                this.error =
                    err?.error?.detail ||
                    'Unable to save attendance.';
            }
        });
    }

    remove(id: number): void {
        if (!id) {
            return;
        }

        this.error = '';

        this.api.deleteAttendance(id).subscribe({
            next: () => {
                this.load();
            },
            error: (err) => {
                console.error('Attendance delete error:', err);
                this.error =
                    err?.error?.detail ||
                    'Unable to delete attendance.';
            }
        });
    }
}