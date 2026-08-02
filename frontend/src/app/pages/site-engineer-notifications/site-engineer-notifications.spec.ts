import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SiteEngineerNotifications } from './site-engineer-notifications';

describe('SiteEngineerNotifications', () => {
  let component: SiteEngineerNotifications;
  let fixture: ComponentFixture<SiteEngineerNotifications>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SiteEngineerNotifications],
    }).compileComponents();

    fixture = TestBed.createComponent(SiteEngineerNotifications);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
