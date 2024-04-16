import {Composition} from 'remotion';
import {MyComposition, TimelineLength} from './Composition';
import item_data from '../../../../guide.json';

export const RemotionRoot: React.FC = () => {
	let totalLength = 0;
	const compositions = item_data.map((item, index) => {
		totalLength += TimelineLength(item);
		return (
			<Composition
				id={item.item.replace(/[^a-zA-Z0-9]/g, '')}
				component={MyComposition}
				defaultProps={item}
				durationInFrames={TimelineLength(item)}
				fps={60}
				width={1080}
				height={1920}
			/>
		);
	});
	console.log('Total length:', Math.round(totalLength / 60 / 60), 'minutes');
	return <>{compositions}</>;
};
