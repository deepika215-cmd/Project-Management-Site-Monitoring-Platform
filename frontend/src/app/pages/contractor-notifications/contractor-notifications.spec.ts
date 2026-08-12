import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractorNotifications } from './contractor-notifications';

describe('ContractorNotifications', () => {
  let component: ContractorNotifications;
  let fixture: ComponentFixture<ContractorNotifications>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContractorNotifications],
    }).compileComponents();

    fixture = TestBed.createComponent(ContractorNotifications);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
