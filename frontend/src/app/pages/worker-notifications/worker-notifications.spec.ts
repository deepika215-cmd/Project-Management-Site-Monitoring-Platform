import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkerNotifications } from './worker-notifications';

describe('WorkerNotifications', () => {
  let component: WorkerNotifications;
  let fixture: ComponentFixture<WorkerNotifications>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkerNotifications],
    }).compileComponents();

    fixture = TestBed.createComponent(WorkerNotifications);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
