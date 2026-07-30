import { Component } from '@angular/core';
import { ProjectAddComponent } from '../project-add/project-add.component';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [ProjectAddComponent],
  templateUrl: './project-list.component.html',
  styleUrl: './project-list.component.scss'
})
export class ProjectListComponent {

}
