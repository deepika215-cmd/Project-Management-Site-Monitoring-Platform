import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SiteEngineerDashboardComponent } from './site-engineer-dashboard.component';

describe('SiteEngineerDashboardComponent', () => {
  let component: SiteEngineerDashboardComponent;
  let fixture: ComponentFixture<SiteEngineerDashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SiteEngineerDashboardComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SiteEngineerDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
