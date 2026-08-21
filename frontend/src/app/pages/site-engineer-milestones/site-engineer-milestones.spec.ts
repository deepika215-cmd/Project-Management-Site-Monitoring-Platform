import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SiteEngineerMilestones } from './site-engineer-milestones';

describe('SiteEngineerMilestones', () => {
  let component: SiteEngineerMilestones;
  let fixture: ComponentFixture<SiteEngineerMilestones>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SiteEngineerMilestones],
    }).compileComponents();

    fixture = TestBed.createComponent(SiteEngineerMilestones);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
